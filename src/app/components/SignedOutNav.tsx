"use client"; // Required for hooks in Next.js App Router

import { usePathname } from "next/navigation"; // Detects the current path
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { FiMoon, FiSun } from "react-icons/fi"; // Search, dark mode, logout



export default function SignedOutNav() {
  const { theme, setTheme } = useTheme(); // Get the current theme
  const [mounted, setMounted] = useState(false); // Prevents hydration mismatch
  const pathname = usePathname(); // Get the current route

  useEffect(() => {
    setMounted(true); // Ensures component is mounted before showing icons
  }, []);

  function handleClick() {
    console.log("Current theme:", theme);
    setTheme(theme === "dark" ? "light" : "dark")
  }

  return (
    <nav className="flex justify-end border-b bg-[#C41230] dark:bg-gray-800">
      {/* Right Section: Upload Button, dark mode, logout */}
        <div className="cursor-pointer">
        {mounted && (
            <button
              onClick={handleClick}
              className="flex items-center justify-center w-20 h-20 mr-6 rounded-md cursor-pointer"
            >
              {theme === "dark" ? (
                <FiSun className="text-yellow-400" size={18} /> // Sun icon for Light mode
              ) : (
                <FiMoon className="text-gray-600 dark:text-white" size={18} /> // Moon icon for Dark mode
              )}
            </button>
        )}
        </div>
    </nav>
  );
}
