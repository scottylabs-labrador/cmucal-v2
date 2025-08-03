use hurl::{
    runner::{self, CaptureResult, HurlResult, RunnerOptionsBuilder, Value, VariableSet},
    util::logger::LoggerOptionsBuilder,
};
use lazy_static::lazy_static;
use regex::Regex;
use scraper::Html;
use std::str::FromStr;

lazy_static! {
    static ref NEWLINES_AND_SPACES: Regex = Regex::new(r"[\r\n]+\s*").unwrap();
    static ref WHITESPACE: Regex = Regex::new(r"\s+").unwrap();
}

/// Inserts a string variable into a [`VariableSet`]
///
/// # Arguments
/// * `vars` - The [`VariableSet`] to modify
/// * `key` - The name of the variable
/// * `value` - The string value to insert
///
/// # Panics
/// If the variable insertion fails
pub fn insert_variable(vars: &mut VariableSet, key: &str, value: &str) {
    vars.insert(key.to_string(), Value::String(value.to_string()))
        .unwrap_or_else(|_| panic!("Failed to insert variable: {key}"));
}

/// Executes a Hurl script with variables
///
/// # Arguments
/// * `script` - The Hurl script content
/// * `vars` - The variables to use
///
/// # Returns
/// Result containing [`HurlResult`] or error message
pub fn execute_hurl(script: &str, vars: &VariableSet) -> Result<HurlResult, String> {
    let runner_opts = RunnerOptionsBuilder::new().build();
    let logger_opts = LoggerOptionsBuilder::new().verbosity(None).build();

    runner::run(script, None, &runner_opts, vars, &logger_opts)
        .map_err(|e| format!("Hurl execution failed: {e}"))
}

/// Extracts all captures from a [`HurlResult`]
///
/// # Arguments
/// * `result` - The [`HurlResult`] containing captures
///
/// # Returns
/// A vector of references to [`CaptureResult`]
pub fn get_captures(result: &HurlResult) -> Vec<&CaptureResult> {
    result
        .entries
        .iter()
        .flat_map(|e| e.captures.iter())
        .collect()
}

/// Extracts the raw HTML body from captures
///
/// # Arguments
/// * `captures` - A vector of [`CaptureResult`] references
///
/// # Returns
/// The parsed [`Html`] document
pub fn parse_from_raw_html(captures: Vec<&CaptureResult>) -> Html {
    let raw_body = captures
        .iter()
        .find(|c| c.name == "raw_body")
        .and_then(|c| match &c.value {
            Value::String(s) => Some(s.as_str()),
            _ => None,
        })
        .unwrap_or("");

    Html::parse_document(raw_body)
}

/// Gets a capture value from a [`HurlResult`]
///
/// # Arguments
/// * `result` - The [`HurlResult`] to extract from
/// * `capture_name` - Name of the capture to find
///
/// # Returns
/// `Some(value)` if found, `None` otherwise
pub fn get_capture_value<'a>(result: &'a HurlResult, capture_name: &'a str) -> Option<&'a Value> {
    get_captures(result)
        .iter()
        .find(|capture| capture.name == capture_name)
        .map(|capture| &capture.value)
}

/// Gets an optional string value from a [`HurlResult`]
///
/// # Arguments
/// * `result` - The [`HurlResult`] to extract from
/// * `capture_name` - Name of the capture to find
///
/// # Returns
/// `Some(value)` if found, `None` otherwise
pub fn get_optional_string_value<'a>(
    result: &'a HurlResult,
    capture_name: &'a str,
) -> Option<String> {
    get_capture_value(result, capture_name).and_then(|value| match value {
        Value::String(s) => {
            let trimmed = s.trim().to_owned();
            let trimmed = NEWLINES_AND_SPACES.replace_all(&trimmed, "");
            let trimmed = WHITESPACE.replace_all(&trimmed, " ").to_string();

            (!trimmed.is_empty() && trimmed != "None").then_some(trimmed)
        }
        _ => None,
    })
}

/// Gets a parsed struct value from a [`HurlResult`]
///
/// # Arguments
/// * `result` - The [`HurlResult`] to extract from
/// * `capture_name` - Name of the capture to find
///
/// # Returns
/// The parsed struct value or the default value if not found or parsing fails
pub fn get_parsed_struct_value<T>(result: &HurlResult, capture_name: &str) -> T
where
    T: Default + FromStr,
{
    get_capture_value(result, capture_name)
        .map(|v| v.to_string().trim().to_owned())
        .unwrap_or_default()
        .parse()
        .unwrap_or_else(|_| T::default())
}

/// Zips two capture lists together
///
/// # Arguments
/// * `result` - The [`HurlResult`] containing captures
/// * `list1_name` - Name of the first list capture
/// * `list2_name` - Name of the second list capture
///
/// # Returns
/// Vector of paired values if both lists exist and have the same length, empty vector otherwise
pub fn zip_captures<F, T>(
    result: &HurlResult,
    list1_name: &str,
    list2_name: &str,
    transform: F,
) -> Vec<T>
where
    F: Fn((&Value, &Value)) -> Option<T>,
{
    if let Some(Value::List(list1)) = get_capture_value(result, list1_name)
        && let Some(Value::List(list2)) = get_capture_value(result, list2_name)
        && list1.len() == list2.len()
    {
        return list1
            .iter()
            .zip(list2.iter())
            .filter_map(transform)
            .collect();
    }

    Vec::new()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_insert_variable() {
        let mut vars = VariableSet::new();

        // Test successful insertion
        insert_variable(&mut vars, "test", "value");
        assert!(matches!(
            vars.get("test").map(|v| v.value()),
            Some(Value::String(_))
        ));
    }
}
