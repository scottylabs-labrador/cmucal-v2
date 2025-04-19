"use client";

import { useState } from "react";
import ThemeProvider from "@components/ThemeProvider";
import Navbar from "@components/Navbar";
import SignedOutNav from "@components/SignedOutNav";
import Welcome from "@components/Welcome";
import { SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { GcalEventsContext } from "../../context/GCalEventsContext";

export default function ClientWrapper({ children }: { children: React.ReactNode }) {
  const [gcalEvents, setGcalEvents] = useState<any[]>([]);

  return (
    <GcalEventsContext.Provider value={{ gcalEvents, setGcalEvents }}>
      <ThemeProvider>
        <SignedIn>
          <Navbar UserButton={<UserButton />} />
        </SignedIn>
        <SignedOut>
          <SignedOutNav />
        </SignedOut>

        <main>
          <SignedIn>{children}</SignedIn>
          <SignedOut>
            <div className="flex justify-center items-center h-[80vh] dark:bg-gray-700">
              <Welcome />
            </div>
          </SignedOut>
        </main>
      </ThemeProvider>
    </GcalEventsContext.Provider>
  );
}
