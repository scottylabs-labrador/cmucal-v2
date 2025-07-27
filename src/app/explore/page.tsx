"use client";
import { useState, useEffect } from "react";
import { useUser } from "@clerk/nextjs";
import axios from "axios";

import TwoColumnLayout from "@components/TwoColumnLayout";
import Calendar from "@components/Calendar";
import SearchResultsSidebar from "@components/SearchResultSidebar";
import { EventType } from "../types/EventType";
import ModalEvent from "../components/ModalEvent";


export default function ExplorePage() {
  const { user } = useUser();
  const [events, setEvents] = useState<EventType[]>([]);
  const [calendarEvents, setCalendarEvents] = useState([]);
  const [eventId, setEventId] = useState<string>("");

  async function fetchCalendarEvents() {
    // get user saved events
    const savedResponse = await axios.get("http://localhost:5001/api/events/user_saved_event_occurrences", {
      params: {
        user_id: user?.id,
      },
      withCredentials: true,
    })
    setCalendarEvents(savedResponse.data)
  };

  useEffect(() => {
    async function fetchEvents() {
      // get all events
      const allResponse = await axios.get("http://localhost:5001/api/events", {
        params: {
          user_id: user?.id,
        }, 
        withCredentials: true,         
      });
      setEvents(allResponse.data)
    };
    fetchEvents()
    fetchCalendarEvents()
  }, []); 


  const toggleAdded = async (thisId: string) => {
    const updatedEvents = [...events];
    const index = updatedEvents.findIndex((e) => e.id === thisId);
    const event = updatedEvents[index];

    if (!event) return;

    // 1. Toggle locally - update attribute
    event.user_saved = !event.user_saved;
    setEvents(updatedEvents);

    // 2. Update the User_saved_events table in database
    try {
      if (event.user_saved) {
        // Add the event to current user's calendar
        await axios.post("http://localhost:5001/api/events/user_saved_events", {
          user_id: user?.id,
          event_id: event.id,
          google_event_id: event.id, // [Q|TODO] is google event id needed in this table
        }, {
          withCredentials: true,
        }); 
      } else {
        // Remove the event from current user's calendar
        await axios.delete(`http://localhost:5001/api/events/user_saved_events/${event.id}`, {
          data: {
          user_id: user?.id,
          google_event_id: event.id, // [Q|TODO] is google event id needed in this table
        },
          withCredentials: true,
        });
      }
    } catch (err) {
      console.error("Error saving / unsaving the event, ", err);
    }

    // 3. Update calendar view
    fetchCalendarEvents();

    // 4. Sync with Google Calendar
    try {
      if (event.user_saved) {
        // Add to Google Calendar via backend
        await axios.post("http://localhost:5001/api/google/calendar/events/add", {
          user_id: user?.id,
          local_event_id: event.id,
          title: event.title,
          start: event.start_datetime,
          end: event.end_datetime,
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
    <TwoColumnLayout
      leftContent={<SearchResultsSidebar events={events} setEvents={setEvents} toggleAdded={toggleAdded} setEventId={setEventId}/>}
      rightContent={<Calendar events={calendarEvents}  setEvents={setEvents} setEventId={setEventId}/>}
    />
    
    <ModalEvent 
      show={eventId ? true : false} 
      onClose={() => setEventId("")}  
      eventId={eventId}
      toggleAdded={toggleAdded}>
    </ModalEvent>
    </div>
  );
}
