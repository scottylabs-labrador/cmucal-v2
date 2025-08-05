use chrono::{Datelike, Utc};
use serde::Serialize;
use std::{
    collections::HashMap,
    fmt::{Display as FmtDisplay, Formatter, Result as FmtResult},
    hash::Hash,
    num::ParseIntError,
    ops::Deref,
    str::FromStr,
};
use strum::{
    AsRefStr, Display, EnumIter, EnumProperty, EnumString, IntoEnumIterator, IntoStaticStr,
};

/// Type alias for a map that associates course metadata with file URLs
pub type SyllabusMap = HashMap<(Year, Season, String, String), String>;

#[derive(
    Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, EnumString, EnumIter, AsRefStr, EnumProperty,
)]
pub enum Season {
    #[strum(serialize = "F", props(full = "fall"))]
    Fall,
    #[strum(serialize = "S", props(full = "spring"))]
    Spring,
    #[strum(serialize = "M", props(full = "summer_1"))]
    Summer1,
    #[strum(serialize = "N", props(full = "summer_2"))]
    Summer2,
}

impl Season {
    pub fn as_str(&self) -> &str {
        self.as_ref()
    }

    pub fn as_full_str(&self) -> &'static str {
        self.get_str("full").unwrap_or_default()
    }

    pub fn all() -> Vec<Season> {
        Season::iter().collect()
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize)]
pub struct Year(pub u16);

impl Year {
    pub fn all() -> Vec<Year> {
        let current_year = Utc::now().year() as u16;
        (2018..=current_year).map(Year).collect()
    }
}

impl Deref for Year {
    type Target = u16;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl FromStr for Year {
    type Err = ParseIntError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let year = s.parse()?;
        Ok(Year(year))
    }
}

impl FmtDisplay for Year {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        write!(f, "{:02}", self.0 % 100)
    }
}

#[derive(
    Debug, Clone, Copy, PartialEq, Serialize, Display, EnumString, EnumIter, IntoStaticStr,
)]
pub enum Department {
    CB, BSC, ICT, HCI, CHE, SCS, CMY, MLG, LTI, CEE, INI, CS, ROB, S3D, ECE, EPP, MSC, MEG,
    MSE, NVS, PHY, STA, MCS, CIT, BMD, BUS, ARC, III, DES, BXA, ETC, DRA, MUS, ART, BSA,
    CAS, H00, HSS, ISP, PE, ECO, ENG, HIS, PHI, ML, CST, PSY, CNB, SDS, PPP, PMP, MED,
    AEM, HC, ISM, STU, CMU,
}

impl Department {
    pub fn all() -> Vec<Department> {
        Department::iter().collect()
    }
}
