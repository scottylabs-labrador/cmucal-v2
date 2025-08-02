"use client";
import { formatDate } from "~/app/utils/dateService";
import { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { useUser } from "@clerk/nextjs";

import { EventClickArg } from "@fullcalendar/core"; 
import { EventType } from "../types/EventType";

import React from 'react'
import Select from 'react-select'


type Props = {
  events: EventType[];
  setEvents: (events: EventType[]) => void;
  toggleAdded: (eventId: number) => void;
  setEventId: (eventId: number) => void;
};

type OptionType = {
  value: number;
  label: string;
};

export default function SearchResultsSidebar({ events, setEvents, toggleAdded, setEventId }: Props) {
  const { user } = useUser();
  const [selectedTags, setSelectedTags] = useState<OptionType[]>([]);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [allTags, setAllTags] = useState<{id: number; name: string}[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<EventType[]>([]);

  // fetch tags and convert to Select options
  useEffect(() => {
    const fetchTags = async () => {
      try {
        const res = await axios.get("http://localhost:5001/api/events/tags")
        setAllTags(res.data)
        console.log("Fetched tags:", res.data);
      } catch (err) {
        console.error("Failed to fetch tags", err)
      };
    };
    fetchTags();
  }, []);
  const tagOptions = allTags.map(tag => ({
    value: tag.id,
    label: tag.name,
  }));

  // fetch sidebar events using selected tag IDs
  useEffect(() => {
    const selectedTagIds = selectedTags.map((tag) => tag.value).join(",");
    const fetchEvents = async () => {
      try {
        const res = await axios.get("http://localhost:5001/api/events", {
          params: {
            user_id: user?.id,
            tags: selectedTagIds,
          },
          withCredentials: true,      
        })
        setFilteredEvents(res.data);
      } catch (err) {
      }
    };
    fetchEvents();
  }, [selectedTags])
  
  return (
    <div>
      {/* filter bar */}
      <Select className="rounded mb-4"
        isMulti 
        options={tagOptions} 
        placeholder="Filter by tags..."
        value={selectedTags}
        onChange={(selectedOptions) => setSelectedTags(selectedOptions as OptionType[])}/>

      {/* event cards */}
      <ul className="space-y-3">
        {filteredEvents.map((event) => (
          <li key={event.id} className="p-3 rounded border">
            <p className="text-sm text-gray-400">EVENT</p>
            <p className="text-lg">{event.title}</p>
            <p className="text-base text-gray-500">{formatDate(event.start_datetime)} - {formatDate(event.end_datetime)}</p>
            <p className="text-base text-gray-500">{event.location}</p>
            <button
              onClick={() => toggleAdded(event.id)}
              className={`mt-2 px-3 py-1.5 rounded-lg ${
                event.user_saved ? "bg-blue-300" : "bg-blue-500"
              } text-white`}
            >
              {event.user_saved ? "Remove" : "Add"}
            </button>
            <button
              onClick={() => {setEventId(event.id)}} // triggers event modal
              className="mt-2 mx-2 px-3 py-1.5 rounded-lg bg-gray-200">
              Learn more
            </button>
          </li>
        ))}
      </ul>

      
    </div>
  );
}
