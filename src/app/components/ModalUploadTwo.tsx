"use client";
import { useRef, useState, useEffect } from "react";
import {
  TextField,
  Autocomplete,
  Chip,
  FormControlLabel,
  Checkbox,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Typography,
  Box,
  Button,
  FormLabel,
  Radio,
  RadioGroup,
  SelectChangeEvent,
} from "@mui/material";
import {
  DatePicker,
  TimePicker,
  LocalizationProvider,
} from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import dayjs, { Dayjs } from "dayjs";

import axios from 'axios';
import { useUser } from "@clerk/nextjs";
import { set } from "lodash";
import { start } from "repl";


interface ModalProps {
  show: boolean;
  onClose: () => void;
  selectedCategory?: any; // Optional prop for selected category
}

type Tag = { id?: string; name: string };

const eventTypesDict = {"Academic": "ACADEMIC", "Career": "CAREER", "Club": "CLUB"};
type EventTypeLabel = keyof typeof eventTypesDict;
type EventTypeValue = typeof eventTypesDict[EventTypeLabel];

const weekdays = ["S", "M", "T", "W", "T", "F", "S"];

interface PayloadType {
  title: string;
  description?: string;
  start_datetime?: string | null;
  end_datetime?: string | null;
  is_all_day?: boolean;
  location: string;
  source_url?: string;
  event_type: string;
  category_id: number;
  org_id: string;
  event_tags?: string[];
  course_num?: string;
  course_name?: string;
  instructors?: string[];
  host?: string;
  link?: string;
  registration_required?: boolean;
}



export default function ModalUploadTwo({ show, onClose, selectedCategory }: ModalProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { user } = useUser();  // clerk user object

  const [selectedEventType, setSelectedEventType] = useState<string>("");
  const [eventTypeError, setEventTypeError] = useState(false);

  const [gcalLink, setGcalLink] = useState("");

  const [title, setTitle] = useState("");
  const [titleError, setTitleError] = useState(false);
  const [location, setLocation] = useState("");
  const [locationError, setLocationError] = useState(false);
  const [sourceURL, setSourceURL] = useState("");
  const [sourceURLError, setSourceURLError] = useState(false);
  const [description, setDescription] = useState("");

  const [selectedTags, setSelectedTags] = useState<Tag[]>([]);
  const [predefinedTags, setPredefinedTags] = useState<Tag[]>([]);

  const [date, setDate] = useState<Dayjs | null>(null);
  const [startTime, setStartTime] = useState<Dayjs | null>(null);
  const [endTime, setEndTime] = useState<Dayjs | null>(null);
  const [allDay, setAllDay] = useState(false);
  const [repeat, setRepeat] = useState("none");

  // recurrence settings
  const [interval, setInterval] = useState(1);
  const [frequency, setFrequency] = useState("week");
  const [selectedDays, setSelectedDays] = useState<number[]>([1, 2, 3, 4, 5]); // M-F
  const [ends, setEnds] = useState("never");
  const [endDate, setEndDate] = useState<Dayjs | null>(null);
  const [occurrences, setOccurrences] = useState(13);

  // Career
  const [requireRegistration, setRequireRegistration] = useState(false);
  const [host, setHost] = useState("");

  // Academic
  const [course, setCourse] = useState("none");
  const [courseNum, setCourseNum] = useState("");
  const [courseName, setCourseName] = useState("");

  const [courseError, setCourseError] = useState(false);
  const courses = [
    "15-112: Fundamentals of Programming",
    "15-213: Intro to Computer Systems",
    "15-251: Great Theoretical Ideas",
    "15-281: Artificial Intelligence",
    "15-410: Operating Systems",
    // Manual for now...
  ];
  const [instructors, setInstructors] = useState<string[]>([]);
  const [instructorStr, setInstructorStr] = useState("");

  const toggleDay = (index: number) => {
    setSelectedDays((prev) =>
      prev.includes(index)
        ? prev.filter((d) => d !== index)
        : [...prev, index]
    );
  };


  const [dateError, setDateError] = useState(false);
  const [startError, setStartError] = useState(false);
  const [endError, setEndError] = useState(false);

  const reset = () => {
    setSelectedEventType("");
    setGcalLink("");
    setTitle("");
    setLocation("");
    setSourceURL("");
    setDescription(""); 
    setDate(null);
    setStartTime(null);
    setEndTime(null);
    setAllDay(false);
    setRepeat("none");
    setInterval(1);
    setFrequency("week");
    // the rest of the recurrence settings
    setRequireRegistration(false);
    setHost("");
    setCourse("none");
    setCourseNum("");
    setCourseName("");
    setInstructors([]);
    setInstructorStr("");
    setSelectedTags([]);
  }

  const validate = () => {
    const isEventTypeInvalid = !selectedEventType;
    const isCourseInvalid = selectedEventType === "Academic" && course === "none";
    const isTitleInvalid = !gcalLink.trim() && !title.trim();
    const isDateInvalid = !gcalLink.trim() && !date;
    const isStartInvalid = !gcalLink.trim() && !allDay && !startTime;
    const isEndInvalid = !gcalLink.trim() && !allDay && !endTime;
    const isLocationInvalid = !gcalLink.trim() && !location.trim();

    setEventTypeError(isEventTypeInvalid);
    setCourseError(isCourseInvalid);
    setTitleError(isTitleInvalid);
    setDateError(isDateInvalid);
    setStartError(isStartInvalid);
    setEndError(isEndInvalid);
    setLocationError(isLocationInvalid);

    return !(
      isEventTypeInvalid ||
      isCourseInvalid ||
      isTitleInvalid ||
      isDateInvalid ||
      isStartInvalid ||
      isEndInvalid ||
      isLocationInvalid
    );
  };

  const handleSubmit = async () => {
    const isValid = validate();
    if (!isValid) {
      alert("Please fill in all required fields.");
      return;
    }

    try {
      if (gcalLink.trim()) {
        // If gcalLink is provided, we can skip other fields
        // create a payload with just the gcalLink
      } else {

          const payload : PayloadType = {
            title: title,
            description: description,
            start_datetime: startTime ? startTime.toISOString() : null,
            end_datetime: endTime ? endTime.toISOString() : null,
            is_all_day: allDay,
            location: location,
            source_url: sourceURL,
            event_type: selectedEventType in eventTypesDict
                        ? eventTypesDict[selectedEventType as keyof typeof eventTypesDict]
                        : "",
            category_id: selectedCategory.id,
            org_id: selectedCategory.org_id,
            event_tags: selectedTags.map(tag => tag.name),
          };

          if (allDay && !startTime && !endTime) {
            payload.start_datetime = date ? dayjs(date).startOf('day').toISOString() : null;
            payload.end_datetime = date ? dayjs(date).endOf('day').toISOString() : null;
          }

          if (selectedEventType === "Academic") {
            payload.course_num = courseNum;
            payload.course_name = courseName;
            payload.instructors = instructors;
          } else if (selectedEventType === "Career") {
            payload.host = host;
            payload.link = sourceURL;
            payload.registration_required = requireRegistration;
          } else if (selectedEventType === "Club") {
            // Add any specific fields for Club events if needed
          }

          // need to add the recurrence settings!

          console.log("Submitting payload:", payload);
          
          const res = await axios.post("http://localhost:5001/api/events/create_event", payload, {
            headers: {
              "Content-Type": "application/json"
            },
            withCredentials: true
          });

          if (res.status === 201) {
            alert("Event created successfully!");
            onClose(); // ✅ only close modal if backend call succeeds
          } else {
            alert("Something went wrong while submitting.");
          }
        }
    } catch (err) {
      console.error("Submission error:", err);
      alert("Failed to submit. Please try again.");
    }
  };


  if (!show || !selectedCategory || !user) return null;

  useEffect(() => {
    const fetchTags = async () => {
      try {
        const res = await axios.get("http://localhost:5001/api/events/tags", {
          withCredentials: true, 
        });

        const tags = res.data; // e.g. [{ id: "1", name: "computer science" }, ...]
        setPredefinedTags(
          tags.map((tag: any) => ({
            id: tag.id,
            name: tag.name.toLowerCase(),
          }))
        );
      } catch (err) {
        console.error("Failed to fetch tags", err);
      }
    };

    fetchTags();
  }, []);

  const handleCourseChange = (e: SelectChangeEvent) => {
    const value = e.target.value;
    setCourse(value);
    if (value === "") {
      setCourseError(true);
    } else {
      const [num, ...nameParts] = value.split(": ");
      setCourseNum(num? num.trim() : "");
      setCourseName(nameParts.join("").trim());
      setCourseError(false);
      console.log("courseNum:", courseNum, "courseName:", courseName);
    }
  };

  const handleInstructorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const instructorsList = value.split(",").map((name) => name.trim());
    setInstructors(instructorsList);
    setInstructorStr(value);
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-40 z-40"
        onClick={onClose}
      />

      {/* Modal */}
      <div
        className="fixed inset-0 z-50 flex items-center justify-center"
        onClick={onClose}
      >
        <div
          ref={containerRef}
          className="bg-white dark:bg-gray-900 p-6 rounded-xl shadow-xl max-w-xl w-full max-h-[90vh] overflow-auto relative"
          onClick={(e) => e.stopPropagation()}
        >
          <h2 className="text-xl font-semibold mb-4">
            Upload to {selectedCategory.organization_name} — {selectedCategory.name}
          </h2>

          {/* Event Type */}
          <div className="flex space-x-2 mb-3">
            {['Academic', 'Career', 'Club'].map((eventType) => (
              <button
                key={eventType}
                className={`px-3 py-1 rounded text-sm ${
                  eventType === selectedEventType ? "bg-blue-400" : "bg-blue-200"
                }`}
                onClick={() => setSelectedEventType(eventType)}
              >
                {eventType}
              </button>
            ))}
          </div>

          {eventTypeError && (
            <p className="text-red-500 text-sm mb-4">
              Please select an event type.
            </p>
          )}

          {/* Title */}
          <TextField
            label="Event Title"
            variant="standard"
            required
            fullWidth
            size="medium"
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              if (titleError) setTitleError(false); // clear error on change
            }}
            error={titleError}
            helperText={titleError ? "Title is required" : ""}
            className="mb-6"
          />

          {/* Host */}
          {/* <select className="w-full border px-3 py-2 mb-3 rounded">
            <option>Select a host</option>
          </select> */}

          {/* Date & Time */}
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <Box display="flex" alignItems="center" gap={2} mt={2}>
              <DatePicker
                label="Date"
                value={date}
                onChange={(newDate: Dayjs | null) => {
                  setDate(newDate);
                  setDateError(false);
                }}
                slotProps={{
                  textField: {
                    required: true,
                    error: dateError,
                    helperText: dateError ? "Date is required" : "",
                  },
                }}
              />

              <TimePicker
                label="Start Time"
                value={startTime}
                onChange={(newTime: Dayjs | null) => {
                  setStartTime(newTime);
                  setStartError(false);
                }}
                disabled={allDay}
                slotProps={{
                  textField: {
                    required: !allDay,
                    error: startError,
                    helperText: startError ? "Start time is required" : "",
                  },
                }}
              />

              <Typography>-</Typography>

              <TimePicker
                label="End Time"
                value={endTime}
                onChange={(newTime: Dayjs | null) => {
                  setEndTime(newTime);
                  setEndError(false);
                }}
                disabled={allDay}
                slotProps={{
                  textField: {
                    required: !allDay,
                    error: endError,
                    helperText: endError ? "End time is required" : "",
                  },
                }}
              />
            </Box>

            <Box display="flex" alignItems="center" gap={2} mb={2}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={allDay}
                    onChange={(e) => setAllDay(e.target.checked)}
                  />
                }
                label="All day"
              />

              {selectedEventType == "Career" && 
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={requireRegistration}
                      onChange={(e) => setRequireRegistration(e.target.checked)}
                    />
                  }
                  label="Require registration"
                />
              }
            </Box>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Repeats</InputLabel>
              <Select
                value={repeat}
                label="Repeats"
                onChange={(e) => setRepeat(e.target.value)}
                size="small"
              >
                <MenuItem value="none">Does not repeat</MenuItem>
                <MenuItem value="daily">Daily</MenuItem>
                <MenuItem value="weekly">Weekly</MenuItem>
                <MenuItem value="monthly">Monthly</MenuItem>
                <MenuItem value="weekdays">Every weekday (Monday to Friday)</MenuItem>
              </Select>

            </FormControl>
          </LocalizationProvider>

          {/* Course */}
          {selectedEventType === "Academic" && (
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Course</InputLabel>
              <Select
                value={course}
                label="Course"
                onChange={(e) => handleCourseChange(e)}
                size="small"
                required={selectedEventType === "Academic"}
                error={courseError}
              >
                <MenuItem value="none">xx-xxx: course_name</MenuItem>
                {courses.map((c) => (
                    <MenuItem key={c} value={c}>
                      {c}
                    </MenuItem>
                  ))}
              </Select>
              {courseError && (
                <p className="text-red-500 text-xs mt-1 ml-4">
                  Please select a course.
                </p>
              )}

            </FormControl>
          )}

          {/* Instructors */}
          {selectedEventType === "Academic" && (
            <TextField
              label="Add Instructors (separate names by ,)"
              variant="outlined"
              fullWidth
              value={instructorStr}
              onChange={handleInstructorChange}
              // need to add error message if wrong format
              size="small"
              sx={{ mb: 2 }}
            />
          )}

          {/* Location */}
          <TextField
            label="Add location"
            variant="outlined"
            required
            fullWidth
            value={location}
            onChange={(e) => {
              setLocation(e.target.value);
              if (locationError) setLocationError(false); // clear error on change
            }}
            error={locationError}
            helperText={locationError ? "Location is required" : ""}
            className="my-4"
            size="small"
          />

          {/* Source URL */}
          <TextField
            label="Add Source/Registration URL"
            variant="outlined"
            sx={{ mb: 2, mt: 2 }}
            required={requireRegistration} // Only required for Career
            fullWidth
            size="small"
            value={sourceURL}
            onChange={(e) => {
              setSourceURL(e.target.value);
              if (sourceURLError) setSourceURLError(false);
            }}
            error={requireRegistration && sourceURLError}
            helperText={
              requireRegistration && sourceURLError
                ? "Source URL is required if registration is required"
                : ""
            }
          />

          {/* Host */}
          {selectedEventType === "Career" && (
            <TextField
              label="Add host"
              variant="outlined"
              fullWidth
              size="small"
              value={host}
              sx={{ mb: 2 }}
              onChange={(e) => {
                setHost(e.target.value);
              }}
            />
          )}


          {/* Tags */}
          <Autocomplete
            multiple
            freeSolo
            options={predefinedTags}
            getOptionLabel={(option) => typeof option === 'string' ? option : option.name}
            filterSelectedOptions
            size="small"
            value={selectedTags}
            onChange={(event, newValue) => {
              const normalized = newValue.map((tag) =>
                typeof tag === "string" ? { name: tag.toLowerCase() } : { ...tag, name: tag.name.toLowerCase() }
              );
              setSelectedTags(normalized);
            }}
            renderTags={(value, getTagProps) =>
              value.map((option: Tag, index: number) => {
                const tagProps = getTagProps({ index });
                const { key, ...rest } = tagProps;

                return (
                  <Chip
                    key={key} // explicitly pass the key
                    label={option.name}
                    variant="outlined"
                    {...rest} // spread the remaining props
                  />
                );
              })
            }
            renderInput={(params) => (
              <TextField
                {...params}
                variant="outlined"
                label="Tags"
                placeholder="Add or select a tag"
              />
            )}
            sx={{ mb: 2 }}
          />

          {/* Description */}
          <TextField
            label="Add description"
            variant="outlined"
            fullWidth
            size="small"
            value={description}
            sx={{ mb: 2 }}
            onChange={(e) => {
              setDescription(e.target.value);
            }}
          />
          
          
          <hr className="my-4" />


          {/* Google Calendar Link */}
          <p className="text-sm">Or paste your Google Calendar link below</p>

          <input
            type="text"
            placeholder="https://calendar.google.com/..."
            value={gcalLink}
            onChange={(e) => {
              setGcalLink(e.target.value);
            }}
            className="w-full p-2 border rounded-md mb-2 bg-white dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-1 focus:ring-gray-400 dark:focus:ring-gray-600"
          />

          <p className="text-xs text-gray-400 mb-4">
            Need help? Go to Calendar Settings &gt; Get Sharable Link
          </p>

    

          {/* Buttons */}
          <div className="flex justify-end gap-4">
            <button
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
              onClick={reset}
            >
              Reset
            </button>

            <button
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
              onClick={() => {
                handleSubmit();
              }}
            >
              Continue
            </button>
          </div>

          {/* Close Button */}
          <button
            onClick={onClose}
            className="absolute top-3 right-3 text-gray-400 hover:text-gray-700 dark:hover:text-white"
          >
            &times;
          </button>
        </div>
      </div>
    </>
  );
}
