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


interface ModalProps {
  show: boolean;
  onClose: () => void;
  selectedCategory?: any; // Optional prop for selected category
}

type Tag = { id?: string; name: string };

export default function ModalUploadTwo({ show, onClose, selectedCategory }: ModalProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { user } = useUser();  // clerk user object

  const [selectedEventType, setSelectedEventType] = useState<string | null>(null);
  const [eventTypeError, setEventTypeError] = useState(false);

  const [title, setTitle] = useState("");
  const [titleError, setTitleError] = useState(false);
  const [selectedTags, setSelectedTags] = useState<Tag[]>([]);
  const [predefinedTags, setPredefinedTags] = useState<Tag[]>([]);

  const [date, setDate] = useState<Dayjs | null>(null);
  const [startTime, setStartTime] = useState<Dayjs | null>(null);
  const [endTime, setEndTime] = useState<Dayjs | null>(null);
  const [allDay, setAllDay] = useState(false);
  const [repeat, setRepeat] = useState("none");

  const [dateError, setDateError] = useState(false);
  const [startError, setStartError] = useState(false);
  const [endError, setEndError] = useState(false);

  const validate = () => {
    if (!selectedEventType) {
      setEventTypeError(true);
      alert("Please select an event type: Academic, Career, or Club.");
      return;
    }
    if (!title.trim()) {
      setTitleError(true);
    }
    setDateError(!date);
    setStartError(!allDay && !startTime);
    setEndError(!allDay && !endTime);
  };

  const handleSubmit = async () => {
    validate();
    if (eventTypeError || titleError || dateError || startError || endError) return;
    // Submit the form
    onClose();
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
          <div className="flex space-x-2 mb-4">
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

          {/* Title */}
          <TextField
            label="Event Title"
            variant="standard"
            required
            fullWidth
            value={title}
            onChange={(e) => {
              setTitle(e.target.value);
              if (titleError) setTitleError(false); // clear error on change
            }}
            error={titleError}
            helperText={titleError ? "Title is required" : ""}
            className="mb-3"
          />

          {/* Host */}
          {/* <select className="w-full border px-3 py-2 mb-3 rounded">
            <option>Select a host</option>
          </select> */}

          {/* Date & Time */}
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <Box display="flex" alignItems="center" gap={2} mb={2}>
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
              <Typography color="primary" fontSize="0.875rem">
                Time zone
              </Typography>
            </Box>

            <FormControl fullWidth>
              <InputLabel>Repeats</InputLabel>
              <Select
                value={repeat}
                label="Repeats"
                onChange={(e) => setRepeat(e.target.value)}
              >
                <MenuItem value="none">Does not repeat</MenuItem>
                <MenuItem value="daily">Daily</MenuItem>
                <MenuItem value="weekly">Weekly</MenuItem>
                <MenuItem value="monthly">Monthly</MenuItem>
              </Select>
            </FormControl>
          </LocalizationProvider>

          {/* Location */}
          <input
            className="w-full border px-3 py-2 mb-3 rounded"
            placeholder="Add location"
          />

          {/* Tags */}
          

          <Autocomplete
            multiple
            freeSolo
            options={predefinedTags}
            getOptionLabel={(option) => typeof option === 'string' ? option : option.name}
            filterSelectedOptions
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
                    key={key} // ✅ explicitly pass the key
                    label={option.name}
                    variant="outlined"
                    {...rest} // ✅ spread the remaining props
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
            className="w-full mb-4"
          />

          {/* Source URL */}
          <input
            className="w-full border px-3 py-2 mb-3 rounded"
            placeholder="Add source URL (optional)"
          />

          {/* Description */}
          <textarea
            className="w-full border px-3 py-2 mb-3 rounded"
            placeholder="Add description"
          />

          {/* Require Registration */}
          <label className="flex items-center space-x-2 mb-3">
            <input type="checkbox" />
            <span className="text-xs">require registration</span>
          </label>

          

          {/* Google Calendar Link */}
          <hr className="my-4" />
          <p className="text-sm  mb-4">Or paste your Google Calendar link below</p>

          <input
            type="text"
            placeholder="https://calendar.google.com/"
            className="w-full p-2 border rounded-md mb-2 bg-white dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-1 focus:ring-gray-400 dark:focus:ring-gray-600"
          />

          <p className="text-xs text-gray-400 mb-4">
            Need help? Go to Calendar Settings &gt; Get Sharable Link
          </p>

          {/* Buttons */}
          <div className="flex justify-end gap-4">
            <button
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
              onClick={() => {
                setSelectedEventType(null);
                // Reset other fields if needed
              }}
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
