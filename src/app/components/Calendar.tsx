"use client";

import { useEffect, useState } from "react";
import { FC } from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import { EventInput } from "@fullcalendar/core"; // Import FullCalendar's Event Type

type Props = {
  events: EventInput[];
  onDeleteEvent?: (id: string) => void;
};

const Calendar: FC<Props> = ({ events, onDeleteEvent }) => {
  // Define state with EventInput type
  // const [events, setEvents] = useState<EventInput[]>([]);

  const handleEventClick = (info: any) => {
    const confirmed = confirm(`Delete event "${info.event.title}"?`);
    if (confirmed) {
      info.event.remove(); // Remove from calendar
      if (onDeleteEvent) {
        onDeleteEvent(info.event.id); // Notify parent
      }
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