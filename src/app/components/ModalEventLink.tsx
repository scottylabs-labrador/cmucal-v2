"use client";
import { useRef, useState, useEffect, useMemo } from "react";

import dayjs, { Dayjs } from "dayjs";
import utc from "dayjs/plugin/utc";
import timezonePlugin from "dayjs/plugin/timezone";

dayjs.extend(utc);
dayjs.extend(timezonePlugin);

import axios from 'axios';
import { useUser } from "@clerk/nextjs";
import { useEventState } from "../../context/EventStateContext";
import Modal from './Modal';
import { GCalLinkPayloadType } from "../utils/types";


interface ModalProps {
  show: boolean;
  onClose: () => void;
  selectedCategory?: any; // Optional prop for selected category
}


const eventTypesDict = {"Academic": "ACADEMIC", "Career": "CAREER", "Club": "CLUB"};
type EventTypeLabel = keyof typeof eventTypesDict;
type EventTypeValue = typeof eventTypesDict[EventTypeLabel];



export default function ModalEventLink({ show, onClose, selectedCategory }: ModalProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { user } = useUser();  // clerk user object

  const [selectedEventType, setSelectedEventType] = useState<string>("");
  const [eventTypeError, setEventTypeError] = useState(false);

  const [gcalLink, setGcalLink] = useState("");
  const [gcalLinkError, setGcalLinkError] = useState(false);

  const [selectManual, setSelectManual] = useState(false);
  const [optionError, setOptionError] = useState(false);
  const { openUpload } = useEventState();




  const reset = () => {
    setSelectedEventType("");
    setGcalLink("");
  }

  const validate = () => {
    const isEventTypeInvalid = !selectedEventType;
    const isRightFormat = gcalLink.trim().startsWith("https://calendar.google.com/calendar/ical/");
    const noOptionSelected = !gcalLink && !selectManual;

    setEventTypeError(isEventTypeInvalid);
    setOptionError(noOptionSelected);
    setGcalLinkError(!isRightFormat);

    return !(
      isEventTypeInvalid ||
      noOptionSelected ||
      !isRightFormat
    );
  };


  const handleSubmit = async () => {
    try {
      if (selectManual) {
        openUpload(selectedCategory, selectedEventType);
        return;
      }

      else if (gcalLink.trim()) {
        const isValid = validate();
        if (!isValid) {
          alert("Please fill in all required fields.");
          return;
        }

        const payload : GCalLinkPayloadType = {
          gcal_link: gcalLink,
          org_id: selectedCategory.org_id,
          category_id: selectedCategory.id,
        };

        console.log("Submitting payload:", payload);
          
        const res = await axios.post("http://localhost:5001/api/events/read_gcal_link", payload, {
          headers: {
            "Content-Type": "application/json"
          },
          withCredentials: true
        });

        // for future improvement, will add a page for users to view their uploaded events
        // and then redirect to that page after successful upload
        if (res.status === 201) {
          alert("Events created successfully!");
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


  return (
    <Modal show={show} onClose={onClose}>
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

      {/* GCal Link Input */}
      <div
        className={`w-full cursor-pointer p-4 rounded-md border-2 mb-4 transition-colors
          ${!selectManual && gcalLink ? "border-blue-200 bg-amber-100 dark:bg-gray-800" : "border-gray-300 hover:border-blue-200 hover:bg-amber-100 dark:hover:bg-gray-800"}`}
        onClick={() => {
          setSelectManual(false);
        }}
      >
        <p className="text-md font-medium text-gray-800 dark:text-white mb-2">Read events from an iCal link</p>
        <input
          type="text"
          placeholder="https://calendar.google.com/calendar/ical/..."
          value={gcalLink}
          onChange={(e) => {
            setGcalLink(e.target.value);
          }}
          className="w-full p-2 border rounded-md mb-2 bg-white dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-1 focus:ring-gray-400 dark:focus:ring-gray-600"
        />


        <p className="text-xs text-gray-400 mb-4">
          Need help? Go to Google Calendar &gt; Calendar Settings &gt; copy and paste the "Secret address in iCal format".
        </p>
        {optionError && (
          <p className="text-red-500 text-sm mb-4">
            Please provide a Google Calendar link or select "Manually fill out the form".
          </p>
        )}
        {gcalLinkError && (
          <p className="text-red-500 text-sm mb-4">
            Please enter a valid Google Calendar iCal link.
          </p>
        )}
      </div>

      {/* Manually fill out the form */}
      <div
        onClick={() => {
          setSelectManual(true);
          setGcalLink(""); // mutually exclusive: clear gcal link
        }}
        className={`w-full cursor-pointer p-4 rounded-md border-2 mb-4 transition-colors
          ${selectManual ? "border-blue-200 bg-amber-100 dark:bg-gray-800" : "border-gray-300 hover:border-blue-200 hover:bg-amber-100 dark:hover:bg-gray-800"}`}
      >
        <p className="text-md font-medium text-gray-800 dark:text-white">
          Manually fill out the form
        </p>
      </div>




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
    </Modal>
  );
}
