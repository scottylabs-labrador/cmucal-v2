"use client";
import { formatDate } from "~/app/utils/dateService";
import { useState, useEffect  } from "react";
import axios from "axios";
import { useUser } from "@clerk/nextjs";

import { EventClickArg } from "@fullcalendar/core"; 
import { EventType } from "../types/EventType";

type Props = {
  events: EventType[];
  setEvents: (events: EventType[]) => void;
  toggleAdded: (eventId: string) => void;
  setEventId: (eventId: string) => void;
};


export default function SearchResultsSidebar({ events, setEvents, toggleAdded, setEventId }: Props) {
  const { user } = useUser();

  return (
    <div>
      <ul className="space-y-3">
        {events.map((event) => (
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
