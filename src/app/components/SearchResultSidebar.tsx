"use client";
import { formatDate } from "~/app/utils/dateService";
import { useState } from "react";
import axios from "axios";
import { useUser } from "@clerk/nextjs";

type Event = {
  id: string;
  title: string;
  start: string; // ISO format
  end: string;
  location: string;
  added: boolean;
  classNames: string[];
};

type Props = {
  events: Event[];
  setEvents: (events: Event[]) => void;
};

export default function SearchResultsSidebar({ events, setEvents }: Props) {
  const { user } = useUser();
  const toggleAdded = async (thisId: string) => {
    const updatedEvents = [...events];
    const index = updatedEvents.findIndex((e) => e.id === thisId);
    const event = updatedEvents[index];

    if (!event) return;

    // Toggle locally
    event.added = !event.added;
    setEvents(updatedEvents);


    try {
      if (event.added) {
        // Add to Google Calendar via backend
        await axios.post("http://localhost:5001/api/google/calendar/events/add", {
          user_id: user?.id,
          local_event_id: event.id,
          title: event.title,
          start: event.start,
          end: event.end,
        }, {
          withCredentials: true,
        });        
      } else {
        // Remove from Google Calendar via backend
        await axios.delete(`http://localhost:5001/api/google/calendar/events/${event.id}`, {
          data: {
            user_id: user?.id,
          },
          withCredentials: true,
        });
        
        
      }
    } catch (err) {
      console.error("Error syncing with Google Calendar:", err);
    }
  };

  return (
    <div>
      <ul className="space-y-3">
        {events.map((event) => (
          <li key={event.id} className="p-3 rounded border">
            <p className="text-sm text-gray-400">EVENT</p>
            <p className="text-lg">{event.title}</p>
            <p className="text-base text-gray-500">{formatDate(event.start)} - {formatDate(event.end)}</p>
            <p className="text-base text-gray-500">{event.location}</p>
            <button
              onClick={() => toggleAdded(event.id)}
              className={`mt-2 px-3 py-1.5 rounded-lg ${
                event.added ? "bg-blue-300" : "bg-blue-500"
              } text-white`}
            >
              {event.added ? "Remove" : "Add"}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
