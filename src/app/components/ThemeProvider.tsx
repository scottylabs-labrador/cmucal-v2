"use client"; // This should be client-side

import { ThemeProvider as NextThemesProvider } from "next-themes";
import { useEffect, useState } from "react";

export default function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="opacity-0">Loading...</div>; // Prevent hydration issues
  }

  return <NextThemesProvider attribute="class" defaultTheme="system">{children}</NextThemesProvider>;
}
