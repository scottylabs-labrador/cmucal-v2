use crate::courses::line::Line;
use models::{
    course_data::{ComponentType, CourseComponent, CourseEntry, Meeting, TimeRange},
    syllabus_data::{Season, Year},
    units::Units,
};

fn parse_meetings(
    lines: &[Line],
    instructors: String,
    days: String,
    time_start: String,
    time_end: String,
    building_room: String,
    campus: String,
) -> (Vec<Meeting>, &[Line]) {
    let mut meetings = vec![Meeting {
        days: days.into(),
        time: TimeRange::from_strings(&time_start, &time_end),
        bldg_room: building_room.into(),
        campus,
        instructors: instructors.clone().into(),
    }];

    let mut remaining = lines;

    while let [
        Line::AdditionalMeeting {
            days,
            time_start,
            time_end,
            building_room,
            campus,
        },
        rest @ ..,
    ] = remaining
    {
        meetings.push(Meeting {
            days: days.clone().into(),
            time: TimeRange::from_strings(time_start, time_end),
            bldg_room: building_room.clone().into(),
            campus: campus.to_owned(),
            instructors: instructors.clone().into(),
        });

        remaining = rest;
    }

    (meetings, remaining)
}

fn parse_component(
    lines: &[Line],
    default_title: String,
) -> (CourseComponent, Option<Units>, &[Line]) {
    match lines {
        [
            Line::PrimaryCourseComponent {
                units,
                section,
                days,
                time_start,
                time_end,
                building_room,
                campus,
                instructors,
            },
            rest @ ..,
        ] => {
            let (meetings, remaining) = parse_meetings(
                rest,
                instructors.clone(),
                days.clone(),
                time_start.clone(),
                time_end.clone(),
                building_room.clone(),
                campus.clone(),
            );

            (
                CourseComponent {
                    title: default_title.to_string(),
                    component_type: ComponentType::from(section.clone()),
                    code: section.clone(),
                    meetings,
                },
                Some(Units::from(units.clone())),
                remaining,
            )
        }

        [
            Line::SecondaryCourseComponent {
                section,
                days,
                time_start,
                time_end,
                building_room,
                campus,
                instructors,
            },
            rest @ ..,
        ] => {
            let (meetings, remaining) = parse_meetings(
                rest,
                instructors.clone(),
                days.clone(),
                time_start.clone(),
                time_end.clone(),
                building_room.clone(),
                campus.clone(),
            );

            (
                CourseComponent {
                    title: default_title.to_string(),
                    component_type: ComponentType::from(section.clone()),
                    code: section.clone(),
                    meetings,
                },
                None,
                remaining,
            )
        }

        other => panic!("Expected a CourseComponent line, got: {:?}", other.first()),
    }
}

fn parse_components(
    lines: &[Line],
    header_title: String,
) -> (Vec<CourseComponent>, Option<Units>, &[Line]) {
    let mut components = Vec::new();
    let mut remaining = lines;
    let mut first_units: Option<Units> = None;
    let mut component_titles: Vec<String> = Vec::new();

    while let Some(line) = remaining.first() {
        match line {
            Line::Empty => {
                remaining = &remaining[1..];
            }

            Line::ComponentTitle(title) => {
                component_titles.push(title.trim().to_string());
                remaining = &remaining[1..];
            }

            Line::PrimaryCourseComponent { .. } => {
                let (component, maybe_units, rest) =
                    parse_component(remaining, header_title.clone());

                if first_units.is_none() {
                    first_units = maybe_units;
                }

                components.push(component);
                remaining = rest;
                component_titles.clear();
            }

            Line::SecondaryCourseComponent { .. } => {
                let effective_title = {
                    let non_redundant: Vec<_> = component_titles
                        .iter()
                        .filter(|t| !header_title.contains(*t))
                        .collect();

                    match non_redundant.as_slice() {
                        [] => header_title.clone(),
                        [only] => format!("{header_title}: {only}"),
                        [.., last] => format!("{header_title}: {last}"),
                    }
                };

                let (component, _, rest) = parse_component(remaining, effective_title);
                components.push(component);
                remaining = rest;

                // Clear titles after consuming a component
                component_titles.clear();
            }

            _ => break,
        }
    }

    (components, first_units, remaining)
}

fn parse_course(lines: &[Line], season: Season, year: Year) -> Option<(CourseEntry, &[Line])> {
    let (number, title, header_units, rest) = match lines {
        [Line::CourseHeader { number, title }, rest @ ..] => {
            (number.clone(), title.clone(), None, rest)
        }
        [
            Line::SecondaryCourseHeader {
                number,
                title,
                units,
            },
            rest @ ..,
        ] => (
            number.clone(),
            title.clone(),
            Some(Units::from(units.clone())),
            rest,
        ),
        _ => return None,
    };

    let (components, inferred_units, remaining) = parse_components(rest, title);
    let units = header_units.or(inferred_units).unwrap_or_else(|| {
        eprintln!("Warning: no units found for course {number} - defaulting to VAR");
        Units::VAR
    });

    Some((
        CourseEntry {
            number: number.into(),
            units,
            components,
            season,
            year,
        },
        remaining,
    ))
}

fn parse_courses(lines: &[Line], season: Season, year: Year) -> Vec<CourseEntry> {
    let mut entries = Vec::new();
    let mut remaining = lines;

    while !remaining.is_empty() {
        if let Some((course, rest)) = parse_course(remaining, season, year) {
            entries.push(course);
            remaining = rest;
        } else {
            // Skip unknown lines and keep parsing
            remaining = &remaining[1..];
        }
    }

    entries
}

/// Groups structured lines into full courses.
///
/// This function performs recursive descent on previously typed lines.
///
/// # Arguments
/// * `lines` - A list of [`Line`]s from the first pass.
/// * `season` - The season for this SOC snapshot (e.g., Fall).
/// * `year` - The academic year.
///
/// # Returns
/// A vector of structured [`CourseEntry`]s.
pub fn second_pass(lines: Vec<Line>, season: Season, year: Year) -> Vec<CourseEntry> {
    parse_courses(&lines, season, year)
}

#[cfg(test)]
mod test {
    use crate::courses::{first_pass::parse_line, second_pass::second_pass};
    use models::{
        course_data::{
            BuildingRoom, ComponentType, CourseComponent, CourseEntry, Meeting, TimeRange,
        },
        days::{DaySet, Days},
        syllabus_data::{Season, Year},
        units::Units,
    };

    #[test]
    fn test_parse_course() {
        let input = "\
\tArchitecture\t\t\t\t\t\t\t\t
\t48025\tFirst Year Seminar: Architecture Edition
\t\t\t3.0\tA\tR\t12:30PM\t01:50PM\tMM A14\tPittsburgh, Pennsylvania\tWorkinger
\t48104\tShop Skills
\t\t\tVAR\tA1\tMW\t10:00AM\t10:50AM\tCFA A9\tPittsburgh, Pennsylvania\tHolmes
\t\t\t\tA2\tMW\t10:00AM\t10:50AM\tCFA A9\tPittsburgh, Pennsylvania\tHolmes
\t48214\tGenerative Modeling
\t\t\t9.0\tLec\tTBA\t\t\tDNM DNM\tPittsburgh, Pennsylvania\tBard
\t\t\t\tA\tM\t10:00AM\t10:50AM\tMM 303\tPittsburgh, Pennsylvania\tBard
\t48313\tNew Pedogogies:\t9.0\t\t\t\t\t\t

\t\tUnreasonable Architecture
\t\t\t\tA\tTR\t11:00AM\t12:20PM\tTBD TBD\tPittsburgh, Pennsylvania\tSindi
\t\tNew Pedogogies\t\t\t\t\t\t\t
\t\tStorycraft
\t\t\t\tD\tMW\t11:00AM\t12:20PM\tTBA\tPittsburgh, Pennsylvania\tStone";

        let lines = input
            .lines()
            .map(str::trim_end)
            .map(parse_line)
            .collect::<Vec<_>>();
        let parsed = second_pass(lines, Season::Fall, Year(2025));

        let expected = vec![
            CourseEntry {
                number: "48025".into(),
                units: Units::new(3.0),
                season: Season::Fall,
                year: Year(2025),
                components: vec![CourseComponent {
                    title: "First Year Seminar: Architecture Edition".to_string(),
                    component_type: ComponentType::Section,
                    code: "A".to_string(),
                    meetings: vec![Meeting {
                        days: Days::Days(DaySet::THURSDAY),
                        time: Some(TimeRange::from_strings("12:30PM", "01:50PM").unwrap()),
                        bldg_room: BuildingRoom::Specific("MM".to_string(), "A14".to_string()),
                        campus: "Pittsburgh, Pennsylvania".to_owned(),
                        instructors: "Workinger".into(),
                    }],
                }],
            },
            CourseEntry {
                number: "48104".into(),
                units: Units::VAR,
                season: Season::Fall,
                year: Year(2025),
                components: vec![
                    CourseComponent {
                        title: "Shop Skills".to_string(),
                        component_type: ComponentType::Section,
                        code: "A1".to_string(),
                        meetings: vec![Meeting {
                            days: Days::Days(DaySet::MONDAY | DaySet::WEDNESDAY),
                            time: Some(TimeRange::from_strings("10:00AM", "10:50AM").unwrap()),
                            bldg_room: BuildingRoom::Specific("CFA".to_string(), "A9".to_string()),
                            campus: "Pittsburgh, Pennsylvania".to_owned(),
                            instructors: "Holmes".into(),
                        }],
                    },
                    CourseComponent {
                        title: "Shop Skills".to_string(),
                        component_type: ComponentType::Section,
                        code: "A2".to_string(),
                        meetings: vec![Meeting {
                            days: Days::Days(DaySet::MONDAY | DaySet::WEDNESDAY),
                            time: Some(TimeRange::from_strings("10:00AM", "10:50AM").unwrap()),
                            bldg_room: BuildingRoom::Specific("CFA".to_string(), "A9".to_string()),
                            campus: "Pittsburgh, Pennsylvania".to_owned(),
                            instructors: "Holmes".into(),
                        }],
                    },
                ],
            },
            CourseEntry {
                number: "48214".into(),
                units: Units::new(9.0),
                season: Season::Fall,
                year: Year(2025),
                components: vec![
                    CourseComponent {
                        title: "Generative Modeling".to_string(),
                        component_type: ComponentType::Lecture,
                        code: "Lec".to_string(),
                        meetings: vec![Meeting {
                            days: Days::TBA,
                            time: None,
                            bldg_room: BuildingRoom::DoesNotMeet,
                            campus: "Pittsburgh, Pennsylvania".to_owned(),
                            instructors: "Bard".into(),
                        }],
                    },
                    CourseComponent {
                        title: "Generative Modeling".to_string(),
                        component_type: ComponentType::Section,
                        code: "A".to_string(),
                        meetings: vec![Meeting {
                            days: Days::Days(DaySet::MONDAY),
                            time: Some(TimeRange::from_strings("10:00AM", "10:50AM").unwrap()),
                            bldg_room: BuildingRoom::Specific("MM".to_string(), "303".to_string()),
                            campus: "Pittsburgh, Pennsylvania".to_owned(),
                            instructors: "Bard".into(),
                        }],
                    },
                ],
            },
            CourseEntry {
                number: "48313".into(),
                units: Units::new(9.0),
                season: Season::Fall,
                year: Year(2025),
                components: vec![
                    CourseComponent {
                        title: "New Pedogogies: Unreasonable Architecture".to_string(),
                        component_type: ComponentType::Section,
                        code: "A".to_string(),
                        meetings: vec![Meeting {
                            days: Days::Days(DaySet::TUESDAY | DaySet::THURSDAY),
                            time: Some(TimeRange::from_strings("11:00AM", "12:20PM").unwrap()),
                            bldg_room: BuildingRoom::ToBeDetermined,
                            campus: "Pittsburgh, Pennsylvania".to_owned(),
                            instructors: "Sindi".into(),
                        }],
                    },
                    CourseComponent {
                        title: "New Pedogogies: Storycraft".to_string(),
                        component_type: ComponentType::Section,
                        code: "D".to_string(),
                        meetings: vec![Meeting {
                            days: Days::Days(DaySet::MONDAY | DaySet::WEDNESDAY),
                            time: Some(TimeRange::from_strings("11:00AM", "12:20PM").unwrap()),
                            bldg_room: BuildingRoom::ToBeAnnounced,
                            campus: "Pittsburgh, Pennsylvania".to_owned(),
                            instructors: "Stone".into(),
                        }],
                    },
                ],
            },
        ];

        assert_eq!(parsed, expected);
    }
}
