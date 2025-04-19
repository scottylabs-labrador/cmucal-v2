"use client";
import TwoColumnLayout from "@components/TwoColumnLayout";
import Calendar from "@components/Calendar";
import { useState } from "react";

const searchResults = [
  { id: "1", title: "TartanHacks Hackathon", date: "Feb 2, 10:00AM - Feb 3, 5:00PM", location: "Rangos Auditorium" , added: false },
  { id: "2", title: "CMU AI Conference", date: "March 15, 9:00AM - 4:00PM", location: "Gates 6115", added: false },
];

function SearchResultsSidebar() {
  const [events, setEvents] = useState(searchResults);
  const [filter, setFilter] = useState(""); // State for dropdown filter

  const toggleAdded = (this_id: string) => {
    setEvents(prevEvents =>
      prevEvents.map((event) =>
        event.id === this_id ? { ...event, added : !event.added } : event 
      )
    )
  }

  return (
    <div>
      {/* <h2 className="text-lg font-semibold mb-2">Search Results</h2> */}
      <ul className="space-y-3">
        <select id="exploreFilter" className="border rounded-lg px-3 py-2 bg-white text-gray-700">
          <option value="explore_career"> Career </option>
          <option value="explore_academic"> Academic </option>
          <option value="explore_activity"> Activity </option>
        </select>
        {events.map((event) => (
          <li key={event.id} className="p-3 rounded">
            <p className="text-sm text-gray-400">EVENT</p>
            <p className="text-lg leading-[2.00]">{event.title}</p>
            <p className="text-base text-gray-500 leading-lg">{event.date}</p>
            <p className="text-base text-gray-500 leading-lg">{event.location}</p>
            <button className="mt-2 mr-2 px-3 py-1.5 rounded-md bg-gray-100">Register</button>
            <button className="mr-2 px-3 py-1.5 rounded-md bg-gray-100 ">Learn more</button>
            <button onClick={() => toggleAdded(event.id)}
              className={`mr-2 px-3 py-1.5 rounded-lg ${ event.added ? 'bg-blue-300' : 'bg-blue-500'} text-white`}>
                { event.added ? "Remove" : "Add" }  </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function Explore() {
  return <TwoColumnLayout leftContent={<SearchResultsSidebar />} rightContent={<Calendar />} />;
}
