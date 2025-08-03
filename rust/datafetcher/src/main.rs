use datafetcher::{
    courses::{first_pass::first_pass, second_pass::second_pass},
    util::{
        execute_hurl, get_capture_value, get_captures, get_optional_string_value,
        get_parsed_struct_value, insert_variable, parse_from_raw_html,
    },
};
use futures::future::join_all;
use hurl::runner::VariableSet;
use models::{
    course_data::{CourseEntry, CourseMetadata, CourseObject},
    reservation::{Reservation, Restriction},
    syllabus_data::{Season, Year},
};
use rayon::iter::{IntoParallelIterator, ParallelIterator};
use reqwest::Client;
use scraper::{Html, Selector};
use serde::Serialize;
use std::{collections::HashMap, fs::File, io::Write, str::FromStr, time::Instant};
use tokio::{join, task};

/// Hurl script for retrieving course details
const COURSE_DETAILS_SCRIPT: &str = include_str!("../scripts/course_details.hurl");

/// Extracts the year from the raw SOC text
fn extract_year(text: &str) -> Option<Year> {
    let line = text.lines().nth(3)?;
    let year_str = line.split_whitespace().last()?;
    year_str.parse::<u16>().ok().map(Year)
}

/// Parses related URLs from course detail HTML
fn parse_related_urls(document: &Html) -> Vec<String> {
    let selector = Selector::parse("#course-detail-related-urls a").unwrap();
    document
        .select(&selector)
        .filter_map(|link| link.value().attr("href"))
        .map(|href| href.to_owned())
        .collect()
}

/// Parses restrictions table from course detail HTML
fn parse_reservations(document: &Html) -> Vec<Reservation> {
    let mut reservations_map: HashMap<String, Vec<Restriction>> = HashMap::new();

    let table_selector = Selector::parse("table").unwrap();
    let header_selector = Selector::parse("th").unwrap();
    let row_selector = Selector::parse("tr").unwrap();
    let cell_selector = Selector::parse("td").unwrap();

    for table in document.select(&table_selector) {
        let headers: Vec<String> = table
            .select(&header_selector)
            .map(|th| th.text().collect::<String>().trim().to_lowercase())
            .collect();

        if headers.contains(&"section".to_string()) && headers.contains(&"restriction".to_string())
        {
            for row in table.select(&row_selector) {
                let cells: Vec<_> = row.select(&cell_selector).collect();

                if cells.len() >= 2 {
                    let section = cells[0].text().collect::<String>().trim().to_owned();
                    let restriction_text = cells[1].text().collect::<String>().trim().to_owned();

                    if !section.is_empty() && !restriction_text.is_empty() {
                        let restriction =
                            Restriction::from_str(&restriction_text).unwrap_or_else(|e| {
                                eprintln!("Failed to parse restriction '{restriction_text}': {e}");
                                Restriction {
                                    student_type: None,
                                    restriction_type: None,
                                }
                            });

                        reservations_map
                            .entry(section)
                            .or_default()
                            .push(restriction);
                    }
                }
            }

            break; // only need one table
        }
    }

    reservations_map
        .into_iter()
        .map(|(section, restrictions)| Reservation {
            section,
            restrictions,
        })
        .collect()
}

/// Adds metadata to a course using Hurl script
fn process_course_details(course: CourseEntry) -> CourseObject {
    let mut vars = VariableSet::new();
    insert_variable(&mut vars, "course", &course.number.to_string());
    insert_variable(&mut vars, "season", course.season.as_str());
    insert_variable(&mut vars, "year", &course.year.to_string());

    let result = match execute_hurl(COURSE_DETAILS_SCRIPT, &vars) {
        Ok(result) if result.success => result,
        Ok(_) => {
            return CourseObject {
                course,
                metadata: None,
            };
        }
        Err(e) => {
            eprintln!(
                "Failed to run course details script for course {} ({}{}): {e}",
                course.number.as_full_string(),
                course.season.as_str(),
                course.year
            );
            return CourseObject {
                course,
                metadata: None,
            };
        }
    };

    let special_permission = get_capture_value(&result, "special_permission")
        .map(|v| matches!(v.to_string().trim().to_lowercase().as_str(), "yes"))
        .unwrap_or_default();

    let captures = get_captures(&result);
    let raw_html = parse_from_raw_html(captures);

    let metadata = CourseMetadata {
        related_urls: parse_related_urls(&raw_html),
        special_permission,
        description: get_optional_string_value(&result, "description"),
        prerequisites: get_parsed_struct_value(&result, "prerequisites"),
        corequisites: get_parsed_struct_value(&result, "corequisites"),
        crosslisted: get_parsed_struct_value(&result, "crosslisted"),
        notes: get_optional_string_value(&result, "notes"),
        reservations: parse_reservations(&raw_html),
    };

    CourseObject {
        course,
        metadata: Some(metadata),
    }
}

#[tokio::main]
async fn main() {
    let overall_start = Instant::now();

    println!("Starting data fetching...");

    let course_objs_future = async {
        println!("Fetching course data...");
        let start = Instant::now();
        let client = Client::new();

        let futures = Season::all().into_iter().map(|season| {
            let client = client.clone();
            async move {
                println!("Downloading data for season: {season:?}");
                let url = format!(
                    "https://enr-apps.as.cmu.edu/assets/SOC/sched_layout_{}.dat",
                    season.as_full_str()
                );

                let text = client
                    .get(&url)
                    .send()
                    .await
                    .expect("Request failed")
                    .text()
                    .await
                    .expect("Failed to read body");

                println!("Downloaded {} bytes for season {:?}", text.len(), season);
                (season, text)
            }
        });

        let raw_data = join_all(futures).await;
        println!("All season data downloaded in {:?}", start.elapsed());

        println!("Parsing course data...");
        let parse_start = Instant::now();

        let course_entries = raw_data
            .into_par_iter()
            .map(|(season, text)| {
                let year = extract_year(&text)
                    .unwrap_or_else(|| panic!("Failed to extract year for {season:?}"));
                let lines = first_pass(&text);
                let courses = second_pass(lines, season, year);

                println!(
                    "Parsed {} courses for {} {}",
                    courses.len(),
                    season.as_str(),
                    year
                );
                courses
            })
            .flatten()
            .collect::<Vec<_>>();

        println!(
            "Parsed {} total courses in {:?}",
            course_entries.len(),
            parse_start.elapsed()
        );

        println!("Processing course details...");
        let details_start = Instant::now();

        let course_objs = course_entries
            .into_par_iter()
            .map(process_course_details)
            .collect::<Vec<_>>();

        println!("Processed course details in {:?}", details_start.elapsed());
        println!(
            "Total course data fetching completed in {:?}",
            start.elapsed()
        );

        course_objs
    };

    println!("Waiting for syllabus and course data...");
    let course_objs = course_objs_future.await;

    // ✅ EXPORT TO JSON
    println!("Writing all_courses.json...");
    let file = File::create("all_courses.json").expect("Failed to create JSON file");
    serde_json::to_writer_pretty(file, &course_objs).expect("Failed to write JSON");

    println!(
        "✅ Done! Wrote {} courses to all_courses.json in {:?}",
        course_objs.len(),
        overall_start.elapsed()
    );
}
