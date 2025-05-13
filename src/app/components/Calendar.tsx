"use client";

import { useEffect, useState } from "react";
import { FC } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import { EventClickArg } from "@fullcalendar/core"; 
import { useGcalEvents } from "../../context/GCalEventsContext";
import "../../styles/calendar.css"; 


import { EventInput } from "@fullcalendar/core"; // Import FullCalendar's Event Type
import axios from "axios";
import { useUser } from "@clerk/nextjs";
import FullCalendarCard from "./FullCalendarCard";


type Props = {
  events: EventInput[];
  setEvents: React.Dispatch<React.SetStateAction<any[]>>;
};

const Calendar: FC<Props> = ({ events, setEvents }) => {
  // Define state with EventInput type
  const { gcalEvents } = useGcalEvents();

  const mergedEventsMap = new Map<string, EventInput>();

  // First add gcalEvents (lower priority)
  gcalEvents.forEach(event => {
    // mergedEventsMap.set(event.id as string, event);
    const key = event.id?.toString() || `${event.title}-${event.start}`;
    mergedEventsMap.set(key, event);
  });

  // Then add events (higher priority — will overwrite duplicates)
  events.forEach(event => {
    const key = event.id?.toString() || `${event.title}-${event.start}`;
    mergedEventsMap.set(key, event);
  });

  const mergedEvents = Array.from(mergedEventsMap.values());


  console.log("Merged Events:", mergedEvents);
  // const [mergedEvents, setMergedEvents] = useState(events);
  const { user } = useUser();

  
  const handleEventClick = async (info: EventClickArg) => {
    const confirmed = confirm(`Remove "${info.event.title}" from your calendar?`);
    if (!confirmed) return;

    try {
      // Delete from Google Calendar via backend
      await axios.delete(`http://localhost:5001/api/google/calendar/events/${info.event.id}`, {
        data: {
          user_id: user?.id,
        },
        withCredentials: true,
      });
      

      // Remove from calendar UI immediately
      info.event.remove();

      // Update local state so sidebar reflects it
      setEvents((prev) =>
        prev.map((e) =>
          e.id === info.event.id ? { ...e, added: false } : e
        )
      );
    } catch (error) {
      console.error("Failed to delete event:", error);
      alert("Something went wrong deleting this event.");
    }
  };

  return (
    <div className="-pt-4 p-4 bg-white rounded-lg shadow-md dark:bg-gray-700 dark:text-gray-300">
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        headerToolbar={{
          left: "today prev,next",
          center: "title",
          right: "dayGridMonth,timeGridWeek,timeGridDay",
        }}
        // events={events}
        events={mergedEvents}
        editable={true}
        selectable={true}
        eventClick={handleEventClick}
        eventContent={FullCalendarCard} 
        // height="auto"
        height={600}
        // eventClassNames="text-sm font-semibold p-1 rounded-md"
      />

    </div>
  );
}

export default Calendar;