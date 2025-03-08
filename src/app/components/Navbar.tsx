"use client"; // Required for hooks in Next.js App Router

import { usePathname } from "next/navigation"; // Detects the current path
import Link from "next/link";
import { FiSearch } from "react-icons/fi"; // Search icon
import { FaRegUser } from "react-icons/fa"; // User icon
import { BsCalendar3 } from "react-icons/bs"; // Calendar icon

export default function Navbar() {
  const pathname = usePathname(); // Get the current route

  return (
    <nav className="flex items-center justify-between p-3 border-b bg-white">
      {/* Left Section: User & Search */}
      <div className="flex items-center space-x-2">
        {/* User Icon (Links to Profile Page) */}
        <Link href="/profile">
          <div
            className={`flex items-center justify-center w-10 h-10 rounded-md cursor-pointer
              ${pathname === "/profile" ? "bg-gray-500 text-white" : "bg-gray-200 text-gray-600 hover:bg-gray-300"}
            `}
          >
            <FaRegUser size={18} />
          </div>
        </Link>

        {/* Search Button (Links to Search Page) */}
        <Link href="/explore">
          <div className={`flex items-center justify-center w-10 h-10 bg-gray-200 rounded-md cursor-pointer hover:bg-gray-300
            ${pathname === "/explore" ? "bg-gray-500 text-white" : "bg-gray-200 text-gray-600 hover:bg-gray-300"}`}>
            <FiSearch size={18} />
          </div>
        </Link>

        {/* Term Selector (Not a link, just UI) */}
        <button className="flex items-center px-3 py-2 space-x-2 border rounded-md">
          <BsCalendar3 className="text-gray-600" size={16} />
          <span className="text-sm font-medium">Fall 24</span>
        </button>
      </div>

      {/* Middle Section: Search Bar */}
      <div className="relative flex items-center w-full max-w-md">
        <FiSearch className="absolute left-3 text-gray-500" size={16} />
        <input
          type="text"
          placeholder="Search for a schedule or event..."
          className="w-full p-2 pl-10 border rounded-md focus:outline-none focus:ring-1 focus:ring-gray-400"
        />
      </div>

      {/* Right Section: Upload Button (Links to Upload Page) */}
      <Link href="/upload">
        <button className="px-4 py-2 border rounded-md bg-gray-100 hover:bg-gray-200">
          Upload
        </button>
      </Link>
    </nav>
  );
}
