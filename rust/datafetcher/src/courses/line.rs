use std::fmt::{Display, Formatter};

#[derive(PartialEq, Eq, Debug)]
pub enum Line {
    /// A simple line containing the name of a department. These are associated with the first two
    /// digits of a course number.
    Department(String),
    /// A line that introduces a new course. Note that the title here may not apply to every
    /// `CourseComponent` in the course. In that case, another variant of "CourseHeader" will be
    /// used that also contains units.
    CourseHeader { number: String, title: String },
    /// This version of `CourseHeader` is used when each course component has a different title.
    SecondaryCourseHeader {
        number: String,
        title: String,
        units: String,
    },
    /// Also used when each course component has a different title. This can either be a duplicate
    /// of the `CourseHeader` title, or more specific title for that particular component. They are
    /// followed by the `SecondaryCourseComponent` line.
    ComponentTitle(String),
    /// A component of a course, i.e. lectures and sections. There can be multiple of these for a
    /// course. "Primary" means that these `CourseComponent`s inherit their titles from the course
    /// header, but this is not a requirement for `CourseComponent`s in general. These can have
    /// multiple meetings, and the first one is included in this line.
    PrimaryCourseComponent {
        units: String,         // To become `Units`
        section: String,       // To become `ComponentType` + CourseComponent.code
        days: String,          // To become `Days`
        time_start: String,    // To become `TimeRange.begin`
        time_end: String,      // To become `TimeRange.end`
        building_room: String, // To become `BuildingRoom`
        campus: String,
        instructors: String, // To become `Meeting.instructors`
    },
    /// Any additional components of a course. These will always share the same number of units
    /// as the `PrimaryCourseComponent` they are associated with.
    SecondaryCourseComponent {
        section: String,
        days: String,
        time_start: String,
        time_end: String,
        building_room: String,
        campus: String,
        instructors: String,
    },
    /// An additional meeting time for a `*CourseComponent`. These will always share the same title,
    /// units, and professors as the `*CourseComponent` they are associated with.
    AdditionalMeeting {
        days: String,
        time_start: String,
        time_end: String,
        building_room: String,
        campus: String,
    },
    /// A blank line or whitespace-only
    Empty,
    /// Any line that doesn't match known structure (logged for diagnostics)
    Unknown(String),
}

impl Display for Line {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Line::Department(name) => write!(f, "Department: {name}"),
            Line::CourseHeader { number, title } => {
                write!(f, "CourseHeader: {number} - {title}")
            }
            Line::SecondaryCourseHeader {
                number,
                title,
                units,
            } => {
                write!(f, "SecondaryCourseHeader: {number} - {title} ({units})")
            }
            Line::ComponentTitle(title) => write!(f, "ComponentTitle: {title}"),
            Line::PrimaryCourseComponent { section, .. } => {
                write!(f, "PrimaryCourseComponent: {section}")
            }
            Line::SecondaryCourseComponent { section, .. } => {
                write!(f, "SecondaryCourseComponent: {section}")
            }
            Line::AdditionalMeeting {
                days,
                time_start,
                time_end,
                ..
            } => {
                write!(f, "AdditionalMeeting: {days} at {time_start}-{time_end}")
            }
            Line::Empty => write!(f, "Empty"),
            Line::Unknown(line) => write!(f, "Unknown: {line}"),
        }
    }
}
