// components/ConnectGoogleButton.tsx
"use client";

import { useUser, useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

export function ConnectGoogleButton() {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  const [calendars, setCalendars] = useState<any[]>([]);
  const [message, setMessage] = useState("");
  // "http://localhost:5001/api/google/authorize"

  const checkAuthStatus = async () => {
    const res = await fetch("http://localhost:5001/api/google/calendar/status", {
      credentials: "include",
    });

    console.log(res);

    if (res.ok) {
      const data = await res.json();
      setIsConnected(data.authorized);
    }

    setLoading(false);
  };

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const authorizeGoogle = async () => {
    const redirectUrl = window.location.href;
    window.location.href = `http://localhost:5001/api/google/authorize?redirect=${redirectUrl}`;
  }

  const fetchCalendars = async () => {
    const res = await fetch("http://localhost:5001/api/google/calendars", {
      credentials: "include",
    });

    if (res.status === 401) {
      // Not authorized, redirect to Google OAuth
      window.location.href = "http://localhost:5001/api/google/authorize";
      return;
    }

    const data = await res.json();
    setCalendars(data);
    console.log(data);
  };

  const createEvent = async () => {
    const res = await fetch("http://localhost:5001/api/google/calendar/events", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        summary: "CMUCal Meeting",
        start: "2025-04-20T10:00:00-04:00",
        end: "2025-04-20T11:00:00-04:00",
        calendarId: "primary",
      }),
    });
    const result = await res.json();
    if (result.link) setMessage(`Event created: ${result.link}`);
    else setMessage("Event creation failed");
  };


  return (
    // <button
    //   onClick={authorizeGoogle}
    //   className="bg-blue-600 text-white px-4 py-2 rounded"
    // >
    //   {isConnected ? "Google Calendar Connected" : "Connect Google Calendar"}
    // </button>
    <button
    onClick={authorizeGoogle}
    className="flex items-center px-3 py-2 space-x-2 border rounded-md dark:border-gray-600"
    disabled={loading || isConnected}
  >
    <span className="text-gray-600 dark:text-white">
    {loading ? "Checking..." : isConnected ? "Google Calendar Connected" : "Connect Google Calendar"}
    </span>
  </button>
  );
}
