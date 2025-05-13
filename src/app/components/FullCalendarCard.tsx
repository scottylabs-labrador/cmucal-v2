import React from 'react'
import { EventContentArg } from '@fullcalendar/core';

function FullCalendarCard(eventContent: EventContentArg) {
    return (
      <div className={`w-full`}> 
      {/* ${eventContent.event.allDay ? 'bg-green': 'bg-green'} */}
        <p className="custom-event-text w-full truncate ...">{eventContent.event.title}</p>
        <p className="custom-event-text w-full ">{eventContent.timeText}</p>
      </div>
    )
  }

export default FullCalendarCard;