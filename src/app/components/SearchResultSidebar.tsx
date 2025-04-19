"use client";
import { FC } from "react";
import { formatDate } from "~/utils/dateService";

type Event = {
  id: string;
  title: string;
  start: string;
  end: string;
  allDay?: boolean;
  location: string;
  classNames?: string[];
  added: boolean;
};


type Props = {
  events: Event[];
  toggleAdded: (id: string) => void;
};

const SearchResultsSidebar: FC<Props> = ({ events, toggleAdded }) => {
  return (
    <div>
      <select className="border rounded-lg px-3 py-2 bg-white text-gray-700">
        <option value="explore_career">Career</option>
        <option value="explore_academic">Academic</option>
        <option value="explore_activity">Activity</option>
      </select>
      <ul className="space-y-3 mt-3">
        {events.map(event => (
          <li key={event.id} className="p-3 rounded border">
            <p className="text-sm text-gray-400">EVENT</p>
            <p className="text-lg">{event.title}</p>
            <p className="text-base text-gray-500">{formatDate(event.start)} - {formatDate(event.end)}</p>
            <p className="text-base text-gray-500">{event.location}</p>
            <button className="mt-2 mr-2 px-3 py-1.5 rounded-md bg-gray-100">Register</button>
            <button className="mr-2 px-3 py-1.5 rounded-md bg-gray-100">Learn more</button>
            <button
              onClick={() => toggleAdded(event.id)}
              className={`mr-2 px-3 py-1.5 rounded-lg ${
                event.added ? "bg-blue-300" : "bg-blue-500"
              } text-white`}
            >
              {event.added ? "Remove" : "Add"}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SearchResultsSidebar;
