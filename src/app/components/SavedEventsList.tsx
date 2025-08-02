"use client";

import { formatDate } from "~/app/utils/dateService";
import { EventType } from "../types/EventType";
import { useState } from "react";
import ModalEvent from "./ModalEvent";

type Props = {
  events: EventType[];
};

export default function SavedEventsList({ events }: Props) {
  const [selectedEventId, setSelectedEventId] = useState<string>("");

  return (
    <div>
      <ul className="space-y-3">
        {events?.map((event) => (
          <li key={event.id} className="p-3 rounded border">
            <p className="text-sm text-gray-400">EVENT</p>
            <p className="text-lg">{event.title}</p>
            <div className="mb-2">
              <p className="text-base text-gray-500">
                {formatDate(event.start || event.start_datetime)} - {formatDate(event.end || event.end_datetime)}
              </p>
              {event.location && (
                <p className="text-base text-gray-500">{event.location}</p>
              )}
            </div>
            <button
              onClick={() => setSelectedEventId(event.id)}
              className="mt-2 mx-2 px-3 py-1.5 rounded-lg bg-gray-200"
            >
              Learn more
            </button>
          </li>
        ))}
      </ul>

      {selectedEventId && (
        <ModalEvent
          show={Boolean(selectedEventId)}
          onClose={() => setSelectedEventId("")}
          eventId={selectedEventId}
          toggleAdded={() => {}} // Empty function since we don't need add/remove functionality here
        />
      )}
    </div>
  );
} 