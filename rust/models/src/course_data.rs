// Cleaned-up course_data.rs with database-related code removed

use crate::{
    days::Days,
    requisite::{Prerequisites, Requisites},
    reservation::Reservation,
    syllabus_data::{Season, Year},
    units::Units,
};
use chrono::NaiveTime;
use serde::{Deserialize, Serialize};
use std::{
    fmt::{Display, Formatter, Result as FmtResult},
    ops::Deref,
    str::FromStr,
};

/// Represents a time range for a meeting
#[derive(Debug, Clone, Copy, PartialEq, Serialize)]
pub struct TimeRange {
    pub begin: NaiveTime,
    pub end: NaiveTime,
}

impl TimeRange {
    pub fn new(begin: NaiveTime, end: NaiveTime) -> Option<Self> {
        (begin < end).then_some(Self { begin, end })
    }

    pub fn from_strings(begin: &str, end: &str) -> Option<Self> {
        let fmt = "%I:%M%p";
        let begin = NaiveTime::parse_from_str(begin, fmt).ok()?;
        let end = NaiveTime::parse_from_str(end, fmt).ok()?;
        Self::new(begin, end)
    }
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub enum BuildingRoom {
    ToBeAnnounced,
    ToBeDetermined,
    DoesNotMeet,
    OffPitt,
    Remote,
    Specific(String, String),
}

impl FromStr for BuildingRoom {
    type Err = ();

    fn from_str(bldg_room: &str) -> Result<Self, Self::Err> {
        match bldg_room {
            "TBA" => Ok(Self::ToBeAnnounced),
            "TBD TBD" => Ok(Self::ToBeDetermined),
            "DNM DNM" => Ok(Self::DoesNotMeet),
            "OFF PITT" => Ok(Self::OffPitt),
            "CMU REMOTE" => Ok(Self::Remote),
            _ => {
                let mut parts = bldg_room.split_whitespace();
                Ok(Self::Specific(
                    parts.next().unwrap_or("").to_string(),
                    parts.collect::<Vec<_>>().join(" "),
                ))
            }
        }
    }
}

impl From<String> for BuildingRoom {
    fn from(bldg_room: String) -> Self {
        Self::from_str(&bldg_room).unwrap()
    }
}

impl Display for BuildingRoom {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        match self {
            Self::Specific(building, room) => write!(f, "{building} {room}"),
            Self::ToBeAnnounced => write!(f, "TBA"),
            Self::ToBeDetermined => write!(f, "TBD"),
            Self::DoesNotMeet => write!(f, "DNM"),
            Self::OffPitt => write!(f, "OFF PITT"),
            Self::Remote => write!(f, "REMOTE"),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct Instructors(Option<Vec<String>>);

impl Deref for Instructors {
    type Target = Option<Vec<String>>;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl FromStr for Instructors {
    type Err = ();

    fn from_str(instructors: &str) -> Result<Self, Self::Err> {
        let instructors = instructors
            .split(',')
            .map(|s| s.trim().to_string())
            .collect::<Vec<_>>();

        if instructors.is_empty() {
            Ok(Self(None))
        } else {
            Ok(Self(Some(instructors)))
        }
    }
}

impl From<&str> for Instructors {
    fn from(s: &str) -> Self {
        Self::from_str(s).unwrap()
    }
}

impl From<String> for Instructors {
    fn from(s: String) -> Self {
        Self::from_str(&s).unwrap()
    }
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct Meeting {
    pub days: Days,
    pub time: Option<TimeRange>,
    pub bldg_room: BuildingRoom,
    pub campus: String,
    pub instructors: Instructors,
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum ComponentType {
    Lecture,
    Section,
}

impl FromStr for ComponentType {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Ok(if s.contains("Lec") {
            Self::Lecture
        } else {
            Self::Section
        })
    }
}

impl From<String> for ComponentType {
    fn from(s: String) -> Self {
        Self::from_str(&s).unwrap()
    }
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct CourseComponent {
    pub title: String,
    pub component_type: ComponentType,
    pub code: String,
    pub meetings: Vec<Meeting>,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct CourseNumber(String);

impl FromStr for CourseNumber {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        if s.len() == 5 && s.chars().all(|c| c.is_ascii_digit()) {
            Ok(Self(s.to_string()))
        } else {
            Err(())
        }
    }
}

impl From<&str> for CourseNumber {
    fn from(num: &str) -> Self {
        Self::from_str(num).unwrap()
    }
}

impl From<String> for CourseNumber {
    fn from(num: String) -> Self {
        Self::from_str(&num).unwrap()
    }
}

impl Display for CourseNumber {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        write!(f, "{}", self.0)
    }
}

impl CourseNumber {
    pub fn as_full_string(&self) -> String {
        let num = &self.0;
        format!("{}-{}", &num[..2], &num[2..])
    }
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct CourseEntry {
    pub number: CourseNumber,
    pub units: Units,
    pub components: Vec<CourseComponent>,
    pub season: Season,
    pub year: Year,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct CourseMetadata {
    pub related_urls: Vec<String>,
    pub special_permission: bool,
    pub description: Option<String>,
    pub prerequisites: Prerequisites,
    pub corequisites: Requisites,
    pub crosslisted: Requisites,
    pub notes: Option<String>,
    pub reservations: Vec<Reservation>,
}

#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct CourseObject {
    pub course: CourseEntry,
    pub metadata: Option<CourseMetadata>,
}
