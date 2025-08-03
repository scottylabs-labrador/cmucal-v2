use serde::{Deserialize, Serialize};
use std::{ops::Deref, str::FromStr};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Expr {
    Course(String),
    And(Box<Expr>, Box<Expr>),
    Or(Box<Expr>, Box<Expr>),
}

impl Expr {
    pub fn evaluate(&self, completed_courses: &[String]) -> bool {
        match self {
            Expr::Course(course) => completed_courses.contains(course),
            Expr::And(left, right) => left.evaluate(completed_courses) && right.evaluate(completed_courses),
            Expr::Or(left, right) => left.evaluate(completed_courses) || right.evaluate(completed_courses),
        }
    }

    pub fn simplify(&self, completed_courses: &[String]) -> Option<Expr> {
        match self {
            Expr::Course(course) => {
                if completed_courses.contains(course) {
                    None
                } else {
                    Some(Expr::Course(course.clone()))
                }
            }
            Expr::And(left, right) => match (left.simplify(completed_courses), right.simplify(completed_courses)) {
                (None, None) => None,
                (Some(l), None) => Some(l),
                (None, Some(r)) => Some(r),
                (Some(l), Some(r)) => Some(Expr::And(Box::new(l), Box::new(r))),
            },
            Expr::Or(left, right) => match (left.simplify(completed_courses), right.simplify(completed_courses)) {
                (None, _) | (_, None) => None,
                (Some(l), Some(r)) => Some(Expr::Or(Box::new(l), Box::new(r))),
            },
        }
    }
}

#[derive(Debug)]
pub struct ParseError(pub String);

impl FromStr for Expr {
    type Err = ParseError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let input = s.trim();

        if input.starts_with('(') && input.ends_with(')') {
            let inner = &input[1..input.len() - 1].trim();
            return inner.parse();
        }

        if let Some(or_parts) = split_top_level(input, "or") {
            if or_parts.len() >= 2 {
                let mut result = or_parts[0].parse()?;
                for part in &or_parts[1..] {
                    result = Expr::Or(Box::new(result), Box::new(part.parse()?));
                }
                return Ok(result);
            }
        }

        if let Some(and_parts) = split_top_level(input, "and") {
            if and_parts.len() >= 2 {
                let mut result = and_parts[0].parse()?;
                for part in &and_parts[1..] {
                    result = Expr::And(Box::new(result), Box::new(part.parse()?));
                }
                return Ok(result);
            }
        }

        if input.chars().all(|c| c.is_ascii_digit()) {
            return Ok(Expr::Course(input.to_string()));
        }

        Err(ParseError(format!("Failed to parse: {input}")))
    }
}

impl From<String> for Expr {
    fn from(s: String) -> Self {
        s.parse().unwrap()
    }
}

fn split_top_level(input: &str, op: &str) -> Option<Vec<String>> {
    let mut result = Vec::new();
    let mut paren_count = 0;
    let mut start = 0;
    let chars: Vec<char> = input.chars().collect();
    let mut i = 0;

    while i < chars.len() {
        match chars[i] {
            '(' => paren_count += 1,
            ')' => paren_count -= 1,
            ' ' if paren_count == 0 && i + op.len() + 2 <= input.len() => {
                let slice = &input[i..i + op.len() + 2];
                if slice.starts_with(' ') && slice[1..].starts_with(op) && slice.ends_with(' ') {
                    let part = input[start..i].trim();
                    if !part.is_empty() {
                        result.push(part.to_string());
                    }
                    i += op.len() + 1;
                    start = i + 1;
                }
            }
            _ => {}
        }
        i += 1;
    }

    let last_part = input[start..].trim();
    if !last_part.is_empty() {
        result.push(last_part.to_string());
    }

    if result.len() >= 2 {
        Some(result)
    } else {
        None
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Default)]
pub struct Prerequisites(Option<Expr>);

impl Prerequisites {
    pub fn into_inner(self) -> Option<Expr> {
        self.0
    }
}

impl FromStr for Prerequisites {
    type Err = ParseError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let req_str = s.trim();
        if req_str == "None" {
            Ok(Prerequisites(None))
        } else {
            req_str.parse().map(|expr| Prerequisites(Some(expr)))
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Default)]
pub struct Requisites(Vec<String>);

impl Deref for Requisites {
    type Target = Vec<String>;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl From<Vec<String>> for Requisites {
    fn from(courses: Vec<String>) -> Self {
        Requisites(courses)
    }
}

impl FromStr for Requisites {
    type Err = ParseError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let req_str = s.trim();
        if req_str == "None" {
            Ok(Requisites(Vec::new()))
        } else {
            let parts = req_str.split(',').map(|s| s.trim().to_string()).collect();
            Ok(Requisites(parts))
        }
    }
}
