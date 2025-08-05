use serde::{Deserialize, Serialize};
use std::fmt::{Display, Formatter, Result as FmtResult};

/// Represents the type of reservation restriction
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum ReservationType {
    /// Reservation for a specific type of student
    StudentType,
    /// Reservation for students in a specific school
    School(String),
    /// Reservation for students with a primary major in a specific major
    PrimaryMajor(String),
}

impl Display for ReservationType {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        match self {
            Self::StudentType => Ok(()),
            Self::School(school) => write!(f, "in {school}"),
            Self::PrimaryMajor(major) => write!(f, "with a primary major in {major}"),
        }
    }
} 
