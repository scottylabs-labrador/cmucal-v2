use crate::courses::line::Line;
use models::units::Units;
use std::str::FromStr;

/// Discard the header rows in the SOC file before parsing
///
/// # Arguments
/// * `input` - A raw string slice containing the full input file contents
///
/// # Returns
/// An iterator over the cleaned, line-based content of the SOC input
fn preprocess_lines(input: &str) -> impl Iterator<Item = &str> {
    input.lines().skip(11).map(str::trim_end)
}

/// Determines whether a string is a valid course number.
///
/// # Arguments
/// * `s` - A string slice to check.
///
/// # Returns
/// `true` if the input is a 5-digit numeric string (e.g., `"15122"`), `false` otherwise.
fn is_course_number(s: &str) -> bool {
    s.len() == 5 && s.chars().all(|c| c.is_ascii_digit())
}

/// Determines whether a string looks like a valid section code.
///
/// # Arguments
/// * `s` - A string slice to check.
///
/// # Returns
/// `true` if the input starts with an uppercase ASCII letter, `false` otherwise.
fn is_section_code(s: &str) -> bool {
    let first = s.chars().next();
    first.is_some_and(|c| c.is_ascii_uppercase())
}

/// Determines which [`Line`] variant a single line fits into
///
/// # Arguments
/// * `line` - A line of text from the input file
///
/// # Returns
/// * A [`Line`] enum variant representing the type of line
pub fn parse_line(line: &str) -> Line {
    let trimmed = line.trim();

    if trimmed.is_empty() {
        return Line::Empty;
    }

    // Fields are split by tabs in the schedule of classes
    let fields: Vec<&str> = trimmed.split('\t').collect();
    let leading_tabs = line.chars().take_while(|&c| c == '\t').count();

    match fields.as_slice() {
        // Department line: Only a department name
        [only] if leading_tabs == 1 => Line::Department(only.to_string()),

        // CourseHeader: number + title only
        [number, title] if is_course_number(number) => Line::CourseHeader {
            number: number.to_string(),
            title: title.trim().to_string(),
        },

        // SecondaryCourseHeader: number + title + units
        [number, title, units, ..]
            if is_course_number(number) && Units::from_str(units).is_ok() =>
        {
            Line::SecondaryCourseHeader {
                number: number.to_string(),
                title: title.trim_end_matches(':').trim().to_string(),
                units: units.to_string(),
            }
        }

        // PrimaryCourseComponent: starts with units
        [
            units,
            section,
            days,
            time_start,
            time_end,
            building_room,
            campus,
            instructors,
            ..,
        ] if Units::from_str(units).is_ok() => Line::PrimaryCourseComponent {
            units: units.to_string(),
            section: section.to_string(),
            days: days.to_string(),
            time_start: time_start.to_string(),
            time_end: time_end.to_string(),
            building_room: building_room.to_string(),
            campus: campus.to_string(),
            instructors: instructors.to_string(),
        },

        // SecondaryCourseComponent: starts with section
        [
            section,
            days,
            time_start,
            time_end,
            building_room,
            campus,
            instructors,
            ..,
        ] if is_section_code(section) => Line::SecondaryCourseComponent {
            section: section.to_string(),
            days: days.to_string(),
            time_start: time_start.to_string(),
            time_end: time_end.to_string(),
            building_room: building_room.to_string(),
            campus: campus.to_string(),
            instructors: instructors.to_string(),
        },

        // AdditionalMeeting: days + times + building + campus
        [days, time_start, time_end, building_room, campus, ..] => Line::AdditionalMeeting {
            days: days.to_string(),
            time_start: time_start.to_string(),
            time_end: time_end.to_string(),
            building_room: building_room.to_string(),
            campus: campus.to_string(),
        },

        // AdditionalMeeting with missing campus
        [days, time_start, time_end, building_room, ..] => Line::AdditionalMeeting {
            days: days.to_string(),
            time_start: time_start.to_string(),
            time_end: time_end.to_string(),
            building_room: building_room.to_string(),
            campus: "Unknown Location".to_owned(),
        },

        // ComponentTitle: short string that doesn't match other formats
        [title] if leading_tabs == 2 => Line::ComponentTitle(title.to_string()),

        // Unknown: matches none of the above, log for diagnostics
        _ => {
            println!("Unknown line format: {line}");
            Line::Unknown(line.to_string())
        }
    }
}

/// Converts raw SOC input text into a flat list of structured `Line` variants.
///
/// This function skips the initial header rows using [`preprocess_lines`] and then parses
/// each subsequent line using [`parse_line`] to classify it into one of the variants of the
/// [`Line`] enum (e.g., `CourseHeader`, `PrimaryCourseComponent`, etc.).
///
/// # Arguments
/// * `input` - A raw string slice containing the full SOC file contents.
///
/// # Returns
/// A `Vec<Line>` representing all non-header lines, each classified into its appropriate variant.
pub fn first_pass(input: &str) -> Vec<Line> {
    preprocess_lines(input).map(parse_line).collect()
}

#[cfg(test)]
mod test {
    use crate::courses::first_pass::parse_line;
    use crate::courses::line::Line;

    #[test]
    fn test_parse_line() {
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

        let lines: Vec<&str> = input.lines().collect();

        let expected: Vec<Line> = vec![
            Line::Department("Architecture".into()),
            Line::CourseHeader {
                number: "48025".into(),
                title: "First Year Seminar: Architecture Edition".into(),
            },
            Line::PrimaryCourseComponent {
                units: "3.0".into(),
                section: "A".into(),
                days: "R".into(),
                time_start: "12:30PM".into(),
                time_end: "01:50PM".into(),
                building_room: "MM A14".into(),
                campus: "Pittsburgh, Pennsylvania".into(),
                instructors: "Workinger".into(),
            },
            Line::CourseHeader {
                number: "48104".into(),
                title: "Shop Skills".into(),
            },
            Line::PrimaryCourseComponent {
                units: "VAR".into(),
                section: "A1".into(),
                days: "MW".into(),
                time_start: "10:00AM".into(),
                time_end: "10:50AM".into(),
                building_room: "CFA A9".into(),
                campus: "Pittsburgh, Pennsylvania".into(),
                instructors: "Holmes".into(),
            },
            Line::SecondaryCourseComponent {
                section: "A2".into(),
                days: "MW".into(),
                time_start: "10:00AM".into(),
                time_end: "10:50AM".into(),
                building_room: "CFA A9".into(),
                campus: "Pittsburgh, Pennsylvania".into(),
                instructors: "Holmes".into(),
            },
            Line::CourseHeader {
                number: "48214".into(),
                title: "Generative Modeling".into(),
            },
            Line::PrimaryCourseComponent {
                units: "9.0".into(),
                section: "Lec".into(),
                days: "TBA".into(),
                time_start: "".into(),
                time_end: "".into(),
                building_room: "DNM DNM".into(),
                campus: "Pittsburgh, Pennsylvania".into(),
                instructors: "Bard".into(),
            },
            Line::SecondaryCourseComponent {
                section: "A".into(),
                days: "M".into(),
                time_start: "10:00AM".into(),
                time_end: "10:50AM".into(),
                building_room: "MM 303".into(),
                campus: "Pittsburgh, Pennsylvania".into(),
                instructors: "Bard".into(),
            },
            Line::SecondaryCourseHeader {
                number: "48313".into(),
                title: "New Pedogogies".into(),
                units: "9.0".into(),
            },
            Line::Empty,
            Line::ComponentTitle("Unreasonable Architecture".into()),
            Line::SecondaryCourseComponent {
                section: "A".into(),
                days: "TR".into(),
                time_start: "11:00AM".into(),
                time_end: "12:20PM".into(),
                building_room: "TBD TBD".into(),
                campus: "Pittsburgh, Pennsylvania".into(),
                instructors: "Sindi".into(),
            },
            Line::ComponentTitle("New Pedogogies".into()),
            Line::ComponentTitle("Storycraft".into()),
            Line::SecondaryCourseComponent {
                section: "D".into(),
                days: "MW".into(),
                time_start: "11:00AM".into(),
                time_end: "12:20PM".into(),
                building_room: "TBA".into(),
                campus: "Pittsburgh, Pennsylvania".into(),
                instructors: "Stone".into(),
            },
        ];

        assert_eq!(lines.len(), expected.len(), "Line count mismatch");

        for (i, (line, expected_line)) in lines.iter().zip(expected).enumerate() {
            let parsed = parse_line(line);
            assert_eq!(
                parsed,
                expected_line,
                "Mismatch at line {}:\ninput: {:?}\nparsed: {:?}",
                i + 1,
                line,
                parsed
            );
        }
    }
}
