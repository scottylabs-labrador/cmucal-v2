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

const initialSearchResults = [
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
    added: true,
  },
];

export default function Explore() {
  const [searchResults, setSearchResults] = useState(initialSearchResults);


  const toggleAdded = (id: string) => {
    setSearchResults(prev =>
      prev.map(event =>
        event.id === id ? { ...event, added: !event.added } : event
    ));
  };

  const handleRemoveFromCalendar = (id: string) => {
    setSearchResults(prev =>
      prev.map(event =>
        event.id === id ? { ...event, added: false } : event
      )
    );
  };

  // Convert added events to FullCalendar's format
  const calendarEvents = searchResults
    .filter(event => event.added)
    .map(event => ({
      id: event.id,
      title: event.title,
      start: event.start,
      end: event.end,
      location: event.location,
    }));

  return <TwoColumnLayout 
        leftContent={<SearchResultsSidebar
          events={searchResults}
          toggleAdded={toggleAdded}/>} 
        rightContent={<Calendar events={calendarEvents} onDeleteEvent={handleRemoveFromCalendar}/>} />;
}
