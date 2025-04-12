// components/ConnectGoogleButton.tsx
"use client";

import { useUser, useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

export function ConnectGoogleButton() {
//   const { getToken } = useUser();
  const { getToken } = useAuth();
  const [isConnected, setIsConnected] = useState(false);

  const checkConnection = async () => {
    const token = await getToken();
    const res = await fetch("http://localhost:5001/api/google/calendar/status", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    const data = await res.json();
    setIsConnected(data.hasAccess);
  };

  const handleConnect = async () => {
    const token = await getToken();
    console.log(token);
    const res = await fetch("http://localhost:5001/api/google/oauth/state", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  
    // if (!res.ok) {
    //   const err = await res.json();
    //   console.error("Failed to get state token", err);
    //   return;
    // }
  
    const { state } = await res.json();

    const params = new URLSearchParams({
      client_id: process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID!,
      redirect_uri: "http://localhost:5001/api/google/oauth/callback",
      response_type: "code",
      scope: "https://www.googleapis.com/auth/calendar",
      access_type: "offline",
      state,
      prompt: "consent",
    });

    window.location.href = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
  };

  useEffect(() => {
    checkConnection();
  }, []);

  return (
    <button
      onClick={handleConnect}
      className="bg-blue-600 text-white px-4 py-2 rounded"
    >
      {isConnected ? "Google Calendar Connected" : "Connect Google Calendar"}
    </button>
  );
}
