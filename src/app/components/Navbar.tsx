"use client"; // Required for hooks in Next.js App Router

import { usePathname } from "next/navigation"; // Detects the current path
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import Link from "next/link";
import { FiSearch, FiMoon, FiSun, FiLogOut } from "react-icons/fi"; // Search, dark mode, logout
import { FaRegUser } from "react-icons/fa"; // User icon
import { BsCalendar3 } from "react-icons/bs"; // Calendar icon
import { ReactNode } from "react";
import Modal from "./Modal"; 
import ModalUpload from "./ModalUpload"; 


type NavBarProps = {
  UserButton: ReactNode;
};

export default function Navbar({ UserButton }: NavBarProps) {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);  
  const pathname = usePathname();

  useEffect(() => {
    setMounted(true);
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

        {/* Term Selector (Not a link, just UI) */}
        <button className="flex items-center px-3 py-2 space-x-2 border rounded-md dark:border-gray-600">
          <BsCalendar3 className="text-gray-600 dark:text-white" size={16} />
          <span className="text-sm font-medium">Fall 24</span>
        </button>

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
        {/* Inside Right Section */}
        <button
          onClick={() => setShowScheduleModal(true)}
          className="px-4 py-2 border rounded-md bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500"
        >
          Upload
        </button>

        <button className="flex items-center px-3 py-2 space-x-2">
          <span className="text-gray-600 dark:text-white">Connect to Cal</span>
        </button>
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

    {/* Modal component */}
    <Modal show={showScheduleModal} onClose={() => setShowScheduleModal(false)}>
      <h2 className="text-lg font-semibold mb-4">Choose a schedule</h2>
      <select className="w-full border rounded-md p-2 mb-4">
        <option>CMUCal Events Dashboard</option>
        <option>ScottyLabs</option>
        <option>15-122 Principles of Imperative Computation</option>
        <option>Create New Schedule</option>
      </select>
      <button
        className="px-4 py-2 bg-blue-600 text-white rounded-md w-full"
        onClick={() => {
          setShowScheduleModal(false);
          setShowUploadModal(true);
        }}
      >
        Next
      </button>
    </Modal>

    <ModalUpload show={showUploadModal} onClose={() => setShowUploadModal(false)} />
    </nav>
  );
}
