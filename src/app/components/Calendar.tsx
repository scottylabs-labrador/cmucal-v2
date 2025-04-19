"use client";

import { useEffect, useState } from "react";
import { FC } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import { EventClickArg } from "@fullcalendar/core"; 
import { useGcalEvents } from "../../context/GCalEventsContext";


import { EventInput } from "@fullcalendar/core"; // Import FullCalendar's Event Type
import axios from "axios";
import { useUser } from "@clerk/nextjs";


type Props = {
  events: EventInput[];
};

const Calendar: FC<Props> = ({ events }) => {
  // Define state with EventInput type
  // const [events, setEvents] = useState<EventInput[]>([]);
  const { gcalEvents } = useGcalEvents();
  // const mergedEvents = [...events, ...gcalEvents];
  // console.log("Merged Events:", mergedEvents);
  // const [mergedEvents, setMergedEvents] = useState(events);
  const { user } = useUser();

  // useEffect(() => {
  //   setMergedEvents((prevEvents) => {
  //     // Optional: remove duplicates by event.id
  //     const merged = [...prevEvents, ...gcalEvents];
  //     // const unique = Array.from(new Map(merged.map(e => [e.id, e])).values());
  //     return merged;
  //   });
  //   console.log("Merged Events:", mergedEvents);
  // }, [gcalEvents]);
  
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
    } catch (error) {
      console.error("Failed to delete event:", error);
      alert("Something went wrong deleting this event.");
    }
  };

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
        eventClick={handleEventClick}
        height="auto"
        // eventClassNames="text-sm font-semibold p-1 rounded-md"
      />

    </div>
  );
}

export default Calendar;