use crate::reservation_type::ReservationType;
use serde::Serialize;
use std::{
    fmt::{Display, Formatter, Result as FmtResult},
    str::FromStr,
};
use strum::EnumIter;

/// Represents different types of students that reservations target
#[derive(Debug, Clone, PartialEq, Serialize, EnumIter)]
pub enum StudentType {
    Freshmen,
    Sophomores,
    Juniors,
    Seniors,
    Students,
    GraduateStudents,
    PhdCandidates,
    FifthYearStudents,
}

impl FromStr for StudentType {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "freshmen" => Ok(Self::Freshmen),
            "sophomores" => Ok(Self::Sophomores),
            "juniors" => Ok(Self::Juniors),
            "seniors" => Ok(Self::Seniors),
            "students" => Ok(Self::Students),
            "graduate students" => Ok(Self::GraduateStudents),
            "phd candidates" => Ok(Self::PhdCandidates),
            "5th yr students" => Ok(Self::FifthYearStudents),
            _ => Err(format!("Unknown student type: {s}")),
        }
    }
}

impl Display for StudentType {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        match self {
            Self::Freshmen => write!(f, "Freshmen"),
            Self::Sophomores => write!(f, "Sophomores"),
            Self::Juniors => write!(f, "Juniors"),
            Self::Seniors => write!(f, "Seniors"),
            Self::Students => write!(f, "Students"),
            Self::GraduateStudents => write!(f, "Graduate Students"),
            Self::PhdCandidates => write!(f, "Phd Candidates"),
            Self::FifthYearStudents => write!(f, "5th YR Students"),
        }
    }
}

/// Represents a course reservation restriction
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct Restriction {
    pub student_type: Option<StudentType>,
    pub restriction_type: Option<ReservationType>,
}

impl Display for Restriction {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        match (&self.student_type, &self.restriction_type) {
            (Some(student_type), Some(restriction_type)) => {
                write!(f, "{student_type} {restriction_type}")
            }
            _ => write!(f, "Unknown restriction"),
        }
    }
}

impl FromStr for Restriction {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        const PREFIX: &str = "Some reservations are for ";

        let content = s.strip_prefix(PREFIX).ok_or("Missing expected prefix")?.trim();

        let s = s
            .lines()
            .map(str::trim)
            .filter(|line| !line.is_empty())
            .collect::<Vec<_>>()
            .join(" ");

        if let Some((student_type_str, major_str)) = parse_primary_major_pattern(content) {
            let student_type = StudentType::from_str(student_type_str)?;
            return Ok(Restriction {
                student_type: Some(student_type),
                restriction_type: Some(ReservationType::PrimaryMajor(major_str.to_owned())),
            });
        }

        if let Some((student_type_str, school_str)) = parse_school_pattern(content) {
            let student_type = StudentType::from_str(student_type_str)?;
            return Ok(Restriction {
                student_type: Some(student_type),
                restriction_type: Some(ReservationType::School(school_str.to_owned())),
            });
        }

        if let Ok(student_type) = StudentType::from_str(content) {
            return Ok(Restriction {
                student_type: Some(student_type),
                restriction_type: Some(ReservationType::StudentType),
            });
        }

        Err(format!("Unable to parse reservation: {s}"))
    }
}

fn parse_primary_major_pattern(content: &str) -> Option<(&str, &str)> {
    content.split_once(" with a primary major in ")
        .map(|(student_type, major)| (student_type.trim(), major.trim()))
}

fn parse_school_pattern(content: &str) -> Option<(&str, &str)> {
    content.split_once(" in ")
        .map(|(student_type, school)| (student_type.trim(), school.trim()))
}

/// Represents a course reservation for a section
#[derive(Debug, Clone, PartialEq, Serialize)]
pub struct Reservation {
    pub section: String,
    pub restrictions: Vec<Restriction>,
}
