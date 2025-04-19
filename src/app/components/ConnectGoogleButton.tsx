// components/ConnectGoogleButton.tsx
"use client";

import { useUser, useAuth } from "@clerk/nextjs";
import { useEffect, useState } from "react";

import * as React from 'react';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import ListItemText from '@mui/material/ListItemText';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import Checkbox from '@mui/material/Checkbox';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

// const cals = ['main', 'personal', 'work'];


export function ConnectGoogleButton() {
  // https://mui.com/material-ui/react-select/
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  const [calendars, setCalendars] = useState<string[]>([]); // state for selected calendars
  const [cals, setCals] = useState<string[]>([]); // state for all calendars from api 
  const [message, setMessage] = useState("");
  // "http://localhost:5001/api/google/authorize"

  useEffect(() => {
    // Only runs on mount
    const checkAuthStatus = async () => {
      try {
        const res = await fetch("http://localhost:5001/api/google/calendar/status", {
          credentials: "include",
        });

        if (res.ok) {
          const data = await res.json();
          setIsConnected(true);
          if (cals.length === 0) {
            fetchCalendars();
          }
        }
        
      } catch (err) {
        console.error("Error checking Google auth status:", err);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  useEffect(() => {
    // If we've finished loading and user is NOT connected, redirect to auth
    if (!loading && !isConnected) {
      authorizeGoogle();
    }
  }, [loading, isConnected]);

  const handleChange = (event: SelectChangeEvent<typeof calendars>) => {
    const {
      target: { value },
    } = event;
    setCalendars(
      // On autofill we get a stringified value.
      typeof value === 'string' ? value.split(',') : value,
    );
  };

  const getGoogleConnectionStatus = () => 
    loading ? "Checking..." : isConnected ? "Google Calendar Connected" : "Connect Google Calendar";
  


  const authorizeGoogle = async () => {
    const redirectUrl = window.location.href;
    window.location.href = `http://localhost:5001/api/google/authorize?redirect=${redirectUrl}`;
  }

  const fetchCalendars = async () => {
    const res = await fetch("http://localhost:5001/api/google/calendars", {
      credentials: "include",
    });
  
    if (res.status === 401) {
      window.location.href = "http://localhost:5001/api/google/authorize";
      return;
    }
  
    const data = await res.json();
  
    // Sort order:
    // 1. primary calendar
    // 2. owned calendars (not primary)
    // 3. shared calendars
    const sorted = data.sort((a: any, b: any) => {
      const priority = (cal: any) => {
        if (cal.primary) return 0;
        if (cal.accessRole === "owner") return 1;
        return 2;
      };
      return priority(a) - priority(b);
    });
  
    // Save the sorted calendars (or just summary list if you prefer)
    setCals(sorted.map((cal: any) => cal.summary));
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
  //   <button
  //   className="flex items-center px-3 py-2 space-x-2 border rounded-md dark:border-gray-600"
  //   disabled={loading || isConnected}
  // >
  //   <span className="text-gray-600 dark:text-white">
  //   {loading ? "Checking..." : isConnected ? "Google Calendar Connected" : "Connect Google Calendar"}
  //   </span>
  // </button>
  <div>
  <FormControl sx={{ m: 1, minWidth: 120 }} size="small">
    <Select
      id="demo-multiple-checkbox"
      multiple
      value={calendars}
      onChange={handleChange}
      input={<OutlinedInput />}
      renderValue={(selected) => getGoogleConnectionStatus()}
      // was selected.join(', ')
      displayEmpty
      MenuProps={MenuProps}
      inputProps={{ 'aria-label': 'Without label' }}
      sx={{
        border: "1px solid #f1f1f1",
        '&:focus': {
          border: "1px solid #f1f1f1",
        },
        '& .MuiSelect-icon': {
          display: "none", // hide dropdown arrow
        },
        '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
          border: "1px solid #f1f1f1",
        },
        '&.Mui-focused': {
          boxShadow: "none", // remove focus ring
          border: "1px solid #f1f1f1"
        }
      }}
    >
      {cals.map((name) => (
        <MenuItem
          key={name}
          value={name}
          sx={{
            fontSize: '0.85rem',
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <Checkbox checked={calendars.includes(name)} />
          <ListItemText
            primary={
              <div className="overflow-x-scroll whitespace-nowrap text-sm">
                {name}
              </div>
            }
          />
        </MenuItem>
      ))}

    </Select>
  </FormControl>
</div>

  );
}
