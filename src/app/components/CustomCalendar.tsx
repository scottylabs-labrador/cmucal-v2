"use client";

import { CustomCalendarProps } from "../utils/types";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import interactionPlugin from "@fullcalendar/interaction";
import { EventClickArg } from "@fullcalendar/core";

/**
 * CustomCalendar - A calendar that displays events
 */
const CustomCalendar: React.FC<CustomCalendarProps> = ({ events }) => {
  return (
    <div className="p-4 bg-white rounded-lg shadow-md">
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
        eventClick={(info: EventClickArg) => {
          // When an event is clicked, show more details
          const { title, start, end, extendedProps } = info.event;
          let detailsText = `${title}\n`;

          if (start) detailsText += `Start: ${start.toLocaleString()}\n`;
          if (end) detailsText += `End: ${end.toLocaleString()}\n`;

          if (extendedProps) {
            if (extendedProps.location) detailsText += `Location: ${extendedProps.location}\n`;
            if (extendedProps.instructor) detailsText += `Instructor: ${extendedProps.instructor}\n`;
            if (extendedProps.course_name) detailsText += `Course: ${extendedProps.course_name}\n`;
          }

          alert(detailsText);
        }}
        height="auto"
      />
    </div>
  );
};

export default CustomCalendar; 
