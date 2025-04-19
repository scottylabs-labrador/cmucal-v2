"use client";

import { useEffect, useState } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import { EventInput } from "@fullcalendar/core"; // Import FullCalendar's Event Type

export default function Calendar() {
  // Define state with EventInput type
  const [events, setEvents] = useState<EventInput[]>([]);

  useEffect(() => {
    // Fetch events dynamically (Replace with API call if needed)
    const fetchEvents = async () => {
      const data: EventInput[] = [
        { id: "1", title: "Lecture", start: "2025-03-08T08:00:00", color: "#9b5de5" },
        { id: "2", title: "Office Hours", start: "2025-03-19T13:30:00", end: "2025-03-19T14:30:00", color: "#ff6f61" },
      ];
      setEvents(data);
    };

    fetchEvents();
  }, []);

  return (
    <div className="p-4 bg-white rounded-lg shadow-md dark:bg-gray-700 dark:text-gray-300">
      <FullCalendar
        plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
        initialView="timeGridWeek"
        headerToolbar={{
          left: "today prev,next",
          center: "title",
          right: "dayGridMonth,timeGridWeek,timeGridDay",
        }}
        events={events}
        editable={true}
        selectable={true}
        eventClick={(info) => alert(`Event: ${info.event.title}`)}
        height="auto"
        // eventClassNames="text-sm font-semibold p-1 rounded-md"
      />

    </div>
  );
}
