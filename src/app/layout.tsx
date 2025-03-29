import "~/styles/globals.css";

import {
  ClerkProvider,
  SignInButton,
  SignUpButton,
  SignedIn,
  SignedOut,
  UserButton,
  GoogleOneTap
} from '@clerk/nextjs'
import { Geist, Geist_Mono } from 'next/font/google'

import type { AppProps } from "next/app";

import ThemeProvider from "@components/ThemeProvider";
import { GeistSans } from "geist/font/sans";
import { type Metadata } from "next";
import Navbar from "@components/Navbar";
import Welcome from "./components/Welcome";
import SignedOutNav from "./components/SignedOutNav";

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})


export const metadata: Metadata = {
  title: "CMUCal",
  description: "A scheduling app that consolidates resources and events on campus.",
  icons: [{ rel: "icon", url: "/Favicon.png" }],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <ClerkProvider>
    <html lang="en"> 
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ThemeProvider>
          <SignedIn>
            <Navbar UserButton={<UserButton />} />
          </SignedIn>
          <SignedOut>
            <SignedOutNav />
          </SignedOut>

          <main>
            <SignedIn>
              {children}
            </SignedIn>

            <SignedOut>
              {/* Show a login screen or redirect maybe */}
              <div className="flex justify-center items-center h-[80vh]">
                <Welcome />
              </div>
            </SignedOut>
          </main>
        </ThemeProvider>
      </body>
    </html>
  </ClerkProvider>

  );
}
