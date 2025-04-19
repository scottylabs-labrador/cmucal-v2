"use client";
import TwoColumnLayout from "@components/TwoColumnLayout";
import Calendar from "@components/Calendar";
import { useState } from "react";
import SearchResultsSidebar from "@components/SearchResultSidebar";


// const initialSearchResults = [
//   { id: "1", title: "TartanHacks Hackathon", date: "Feb 2, 10:00AM - Feb 3, 5:00PM", location: "Rangos Auditorium" , added: false },
//   { id: "2", title: "CMU AI Conference", date: "Apr 16, 9:00AM - 4:00PM", location: "Gates 6115", added: false },
//   { id: "3", title: "ScottySpark", date: "Apr 19, 5:00PM - 8:00PM", location: "Swartz Center, Tepper", added: false },
// ];


const initialEvents = [
  {
    id: "1",
    title: "TartanHacks Hackathon",
    start: "2025-02-02T10:00:00",
    end: "2025-02-03T17:00:00",
    location: "Rangos Auditorium",
    added: false,
  },
  {
    id: "2",
    title: "CMU AI Conference",
    start: "2025-04-16T09:00:00",
    end: "2025-04-16T16:00:00",
    location: "Gates 6115",
    added: false,
  },
  {
    id: "3",
    title: "ScottySpark",
    start: "2025-04-19T17:00:00",
    end: "2025-04-19T20:00:00",
    location: "Swartz Center, Tepper",
    added: false,
  },
];

// interface ExplorePageProps {
//   gcalEvents: any[];
//   setGcalEvents: React.Dispatch<React.SetStateAction<any[]>>;
// }

export default function ExplorePage() {
  const [events, setEvents] = useState(initialEvents);

  const calendarEvents = events
    .filter((event) => event.added)
    .map((event) => ({
      id: event.id,
      title: event.title,
      start: event.start,
      end: event.end,
    }));

  const handleEventDelete = (id: string) => {
    const updated = events.map((event) =>
      event.id === id ? { ...event, added: false } : event
    );
    setEvents(updated);
  };

  return (
    <TwoColumnLayout
      leftContent={<SearchResultsSidebar events={events} setEvents={setEvents} />}
      rightContent={<Calendar events={calendarEvents}  setEvents={setEvents}/>}
    />
  );
}
