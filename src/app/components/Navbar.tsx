"use client"; // Required for hooks in Next.js App Router

import { usePathname } from "next/navigation"; // Detects the current path
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import Link from "next/link";
import { FiSearch, FiMoon, FiSun, FiLogOut } from "react-icons/fi"; // Search, dark mode, logout
import { FaRegUser } from "react-icons/fa"; // User icon
import { BsCalendar3 } from "react-icons/bs"; // Calendar icon
import { ReactNode } from "react";
import { ConnectGoogleButton } from "./ConnectGoogleButton";

import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormHelperText from '@mui/material/FormHelperText';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';



type NavBarProps = {
  UserButton: ReactNode;
};

export default function Navbar({ UserButton }: NavBarProps) {
  const { theme, setTheme } = useTheme(); // Get the current theme
  const [mounted, setMounted] = useState(false); // Prevents hydration mismatch
  const [term, setTerm] = useState('Spring 25');

  // const handleTermChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
  //   setTerm(event.target.value);
  // };

  const handleTermChange = (event: SelectChangeEvent) => {
    setTerm(event.target.value);
  };

  const pathname = usePathname(); // Get the current route

  useEffect(() => {
    setMounted(true); // Ensures component is mounted before showing icons
  }, []);

  return (
    <nav className="flex items-center justify-between p-3 border-b bg-white dark:bg-gray-800">
      {/* Left Section: User & Search */}
      <div className="flex items-center space-x-2">
        {/* User Icon (Links to Profile Page) */}
        <Link href="/profile">
          <div
            className={`flex items-center justify-center w-10 h-10 rounded-md cursor-pointer dark:bg-gray-600
              ${pathname === "/profile" ? "bg-gray-500 text-white" : "bg-gray-200 text-gray-600 hover:bg-gray-300"}
            `}
          >
            <FaRegUser className="text-gray-600 dark:text-white" size={18} />
          </div>
        </Link>

        {/* Search Button (Links to Search Page) */}
        <Link href="/explore">
          <div className={`flex items-center justify-center w-10 h-10 rounded-md cursor-pointer dark:bg-gray-600
            ${pathname === "/explore" ? "bg-gray-500 text-white" : "bg-gray-200 text-gray-600 hover:bg-gray-300"}`}>
            <FiSearch className="text-gray-600 dark:text-white" size={18} />
          </div>
        </Link>

        {/* Term Selector Dropdown */}
        {/* <button className="flex items-center px-3 py-2.5 space-x-2 border rounded-md dark:border-gray-600">
          <BsCalendar3 className="text-gray-600 dark:text-white" size={16} />
          <select
            value={term}
            onChange={handleTermChange}
            className="bg-transparent text-sm text-gray-800 dark:text-white focus:outline-none appearance-none"
          >
            <option value="Spring 25">Spring 25</option>
            <option value="Fall 24">Fall 24</option>
          </select>
        </button> */}
        <FormControl sx={{ m: 1, minWidth: 120}} size="small">
        <Select
          value={term}
          onChange={handleTermChange}
          displayEmpty
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
          <MenuItem value={'Spring 25'}>
            <div className="flex items-center space-x-2">
              {term === 'Spring 25' ? (<BsCalendar3 className="text-gray-600 dark:text-white" size={16} />): (<></>)}
              <span className="text-sm text-gray-800 dark:text-white">Spring 25</span>
            </div>
          </MenuItem>
          <MenuItem value={'Fall 24'}>
            <div className="flex items-center space-x-2">
              {term === 'Fall 24' ? (<BsCalendar3 className="text-gray-600 dark:text-white" size={16} />): (<></>)}
              <span className="text-sm text-gray-800 dark:text-white">Fall 24</span>
            </div>
          </MenuItem>
        </Select>
      </FormControl>

        <Link href="/upload">
          <button className="px-4 py-2 border rounded-md bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500">
            Upload
          </button>
        </Link>
      </div>

      {/* Middle Section: Search Bar */}
      <div className="relative flex items-center w-full max-w-md">
        <FiSearch className="absolute left-3 text-gray-500 dark:text-gray-300" size={16} />
        <input
          type="text"
          placeholder="Search for a schedule or event..."
          className="w-full p-2 pl-10 border rounded-md bg-white dark:bg-gray-700 dark:text-white focus:outline-none focus:ring-1 focus:ring-gray-400 dark:focus:ring-gray-500"
        />
      </div>

      {/* Right Section: Upload Button, dark mode, logout */}
      <div className="flex items-center space-x-2">
        {/* <button className="flex items-center px-3 py-2 space-x-2">
          <span className="text-gray-600 dark:text-white">Connect to Cal</span>
        </button> */}
        <ConnectGoogleButton />
        {/* Moon Icon for Dark Mode Toggle */}
        {/* Dark Mode Toggle Button */}
        {mounted && (
            <button
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="flex items-center justify-center w-10 h-10 pl-2 rounded-md cursor-pointer"
            >
              {theme === "dark" ? (
                <FiSun className="text-yellow-400" size={18} /> // Sun icon for Light mode
              ) : (
                <FiMoon className="text-gray-600 dark:text-white" size={18} /> // Moon icon for Dark mode
              )}
            </button>
        )}
        <div>{UserButton}</div>
        {/* <Link href="/" className="flex items-center px-3 py-2 space-x-2">
          <FiLogOut className="text-gray-600 dark:text-white" size={16} />
          <span className="text-sm font-medium">Sign out</span>
        </Link> */}
      </div>
    </nav>
  );
}
