use serde::Serialize;
use std::{
    fmt::{Display, Formatter, Result as FmtResult},
    ops::{BitAnd, BitAndAssign, BitOr, BitOrAssign, Not},
    str::FromStr,
};

/// Represents the days of the week a meeting occurs
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize)]
#[repr(transparent)]
pub struct DaySet(u8);

impl DaySet {
    pub const MONDAY: Self = DaySet(1 << 0);
    pub const TUESDAY: Self = DaySet(1 << 1);
    pub const WEDNESDAY: Self = DaySet(1 << 2);
    pub const THURSDAY: Self = DaySet(1 << 3);
    pub const FRIDAY: Self = DaySet(1 << 4);
    pub const SATURDAY: Self = DaySet(1 << 5);
    pub const SUNDAY: Self = DaySet(1 << 6);

    pub const WEEKDAYS: Self = DaySet(0b0011111);
    pub const WEEKEND: Self = DaySet(0b1100000);
    pub const ALL: Self = DaySet(0b1111111);
    pub const NONE: Self = DaySet(0);

    const DAY_CHARS: [(Self, char); 7] = [
        (Self::MONDAY, 'M'),
        (Self::TUESDAY, 'T'),
        (Self::WEDNESDAY, 'W'),
        (Self::THURSDAY, 'R'),
        (Self::FRIDAY, 'F'),
        (Self::SATURDAY, 'S'),
        (Self::SUNDAY, 'U'),
    ];

    pub fn new() -> Self {
        Self::NONE
    }

    pub fn contains(self, day: Self) -> bool {
        (self & day) == day
    }

    pub fn set(&mut self, day: Self, value: bool) {
        if value {
            *self |= day;
        } else {
            *self &= !day;
        }
    }

    pub fn add(&mut self, day: Self) {
        *self |= day;
    }

    pub fn remove(&mut self, day: Self) {
        *self &= !day;
    }
}

impl FromStr for DaySet {
    type Err = ();

    fn from_str(days: &str) -> Result<Self, Self::Err> {
        let mut result = Self::NONE;

        for c in days.chars() {
            for &(day, day_char) in &Self::DAY_CHARS {
                if c == day_char {
                    result |= day;
                    break;
                }
            }
        }

        Ok(result)
    }
}

impl Display for DaySet {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        let mut result = String::new();

        for &(day, day_char) in &Self::DAY_CHARS {
            if self.contains(day) {
                result.push(day_char);
            }
        }

        write!(f, "{result}")
    }
}

impl BitOr for DaySet {
    type Output = Self;

    fn bitor(self, rhs: Self) -> Self::Output {
        DaySet(self.0 | rhs.0)
    }
}

impl BitAnd for DaySet {
    type Output = Self;

    fn bitand(self, rhs: Self) -> Self::Output {
        DaySet(self.0 & rhs.0)
    }
}

impl Not for DaySet {
    type Output = Self;

    fn not(self) -> Self::Output {
        DaySet((!self.0) & 0x7F)
    }
}

impl BitOrAssign for DaySet {
    fn bitor_assign(&mut self, rhs: Self) {
        self.0 |= rhs.0;
    }
}

impl BitAndAssign for DaySet {
    fn bitand_assign(&mut self, rhs: Self) {
        self.0 &= rhs.0;
    }
}

#[derive(Debug, Clone, Copy, Default, PartialEq, Serialize)]
pub enum Days {
    Days(DaySet),
    #[default]
    TBA,
}

impl Display for Days {
    fn fmt(&self, f: &mut Formatter<'_>) -> FmtResult {
        match self {
            Self::Days(days) => write!(f, "{days}"),
            Self::TBA => write!(f, "TBA"),
        }
    }
}

impl FromStr for Days {
    type Err = ();

    fn from_str(days: &str) -> Result<Self, Self::Err> {
        if days.contains("TBA") {
            Ok(Self::TBA)
        } else {
            DaySet::from_str(days).map(Self::Days)
        }
    }
}

impl From<String> for Days {
    fn from(days: String) -> Self {
        Self::from_str(&days).unwrap_or_default()
    }
}
