use serde::Serialize;
use std::{
    cmp::Ordering,
    fmt::{Display, Formatter, Result as FmtResult},
    str::FromStr,
};

#[derive(Debug, Clone, Serialize, PartialEq)]
pub enum ParseUnitError {
    EmptyInput,
    NoValidUnits,
}

impl Display for ParseUnitError {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        match self {
            Self::EmptyInput => write!(f, "Empty input string"),
            Self::NoValidUnits => write!(f, "No valid units found in input"),
        }
    }
}

fn compare_units(min_a: f32, max_a: f32, min_b: f32, max_b: f32) -> Option<Ordering> {
    match min_a.partial_cmp(&min_b) {
        Some(Ordering::Equal) => max_a.partial_cmp(&max_b),
        other => other,
    }
}

#[derive(Debug, Clone, Serialize, PartialEq)]
pub enum UnitTypeSimple {
    Single(f32),
    Range(f32, f32),
}

impl UnitTypeSimple {
    pub fn min_value(&self) -> f32 {
        match self {
            Self::Single(v) | Self::Range(v, _) => *v,
        }
    }

    pub fn max_value(&self) -> f32 {
        match self {
            Self::Single(v) | Self::Range(_, v) => *v,
        }
    }
}

impl PartialOrd for UnitTypeSimple {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        compare_units(self.min_value(), self.max_value(), other.min_value(), other.max_value())
    }
}

impl Display for UnitTypeSimple {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        match self {
            Self::Single(v) if v.fract() == 0.0 => write!(f, "{}", *v as i32),
            Self::Single(v) => write!(f, "{v}"),
            Self::Range(min, max) if min.fract() == 0.0 && max.fract() == 0.0 => {
                write!(f, "{}-{}", *min as i32, *max as i32)
            }
            Self::Range(min, max) => write!(f, "{min}-{max}"),
        }
    }
}

#[derive(Debug, Clone, Serialize, PartialEq)]
pub enum UnitType {
    Single(f32),
    Range(f32, f32),
    Multi(Vec<UnitTypeSimple>),
}

impl UnitType {
    pub fn min_value(&self) -> f32 {
        match self {
            Self::Single(v) | Self::Range(v, _) => *v,
            Self::Multi(units) => units.iter().map(UnitTypeSimple::min_value).fold(f32::MAX, f32::min),
        }
    }

    pub fn max_value(&self) -> f32 {
        match self {
            Self::Single(v) | Self::Range(_, v) => *v,
            Self::Multi(units) => units.iter().map(UnitTypeSimple::max_value).fold(f32::MIN, f32::max),
        }
    }
}

impl PartialOrd for UnitType {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        compare_units(self.min_value(), self.max_value(), other.min_value(), other.max_value())
    }
}

impl FromStr for UnitType {
    type Err = ParseUnitError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let s = s.trim();
        if s.is_empty() {
            return Err(ParseUnitError::EmptyInput);
        }

        if let Ok(v) = s.parse::<f32>() {
            return Ok(Self::Single(v));
        }

        let mut simple_units = vec![];

        for part in s.split([',', ' '].as_ref()).filter(|s| !s.is_empty()) {
            let trimmed = part.trim();
            if let Some((a, b)) = trimmed.split_once('-') {
                if let (Ok(min), Ok(max)) = (a.parse(), b.parse()) {
                    simple_units.push(UnitTypeSimple::Range(min, max));
                    continue;
                }
            }

            if let Ok(v) = trimmed.parse() {
                simple_units.push(UnitTypeSimple::Single(v));
            }
        }

        if simple_units.is_empty() {
            return Err(ParseUnitError::NoValidUnits);
        }

        if simple_units.len() == 1 {
            return Ok(match &simple_units[0] {
                UnitTypeSimple::Single(v) => Self::Single(*v),
                UnitTypeSimple::Range(min, max) => Self::Range(*min, *max),
            });
        }

        simple_units.sort_by(|a, b| a.partial_cmp(b).unwrap_or(Ordering::Equal));
        Ok(Self::Multi(simple_units))
    }
}

impl From<UnitTypeSimple> for UnitType {
    fn from(simple: UnitTypeSimple) -> Self {
        match simple {
            UnitTypeSimple::Single(v) => Self::Single(v),
            UnitTypeSimple::Range(min, max) => Self::Range(min, max),
        }
    }
}

impl From<String> for UnitType {
    fn from(s: String) -> Self {
        Self::from_str(&s).unwrap()
    }
}

impl Display for UnitType {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        match self {
            Self::Single(v) if v.fract() == 0.0 => write!(f, "{}", *v as i32),
            Self::Single(v) => write!(f, "{v}"),
            Self::Range(min, max) if min.fract() == 0.0 && max.fract() == 0.0 => {
                write!(f, "{}-{}", *min as i32, *max as i32)
            }
            Self::Range(min, max) => write!(f, "{min}-{max}"),
            Self::Multi(units) => {
                let s = units.iter().map(ToString::to_string).collect::<Vec<_>>().join(",");
                write!(f, "{s}")
            }
        }
    }
}

#[derive(Debug, Clone, Serialize, PartialEq)]
pub enum Units {
    VAR,
    Value(UnitType),
}

impl Units {
    pub fn new(value: f32) -> Self {
        Self::Value(UnitType::Single(value))
    }
}

impl PartialOrd for Units {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        match (self, other) {
            (Self::VAR, Self::VAR) => Some(Ordering::Equal),
            (Self::VAR, _) => Some(Ordering::Greater),
            (_, Self::VAR) => Some(Ordering::Less),
            (Self::Value(a), Self::Value(b)) => a.partial_cmp(b),
        }
    }
}

impl FromStr for Units {
    type Err = ParseUnitError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.trim() {
            "" => Err(ParseUnitError::EmptyInput),
            "VAR" => Ok(Self::VAR),
            other => UnitType::from_str(other).map(Self::Value),
        }
    }
}

impl From<UnitType> for Units {
    fn from(unit_type: UnitType) -> Self {
        Self::Value(unit_type)
    }
}

impl From<String> for Units {
    fn from(s: String) -> Self {
        Self::from_str(&s).unwrap()
    }
}

impl Display for Units {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        match self {
            Self::VAR => write!(f, "VAR"),
            Self::Value(unit_type) => write!(f, "{unit_type}"),
        }
    }
}
