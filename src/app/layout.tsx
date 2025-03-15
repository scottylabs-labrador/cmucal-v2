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
      <html lang="en" className={`${GeistSans.variable}`}> 
        <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
          <header className="flex justify-end items-center p-4 gap-4 h-16">
            <SignedOut>
              <SignInButton />
              <SignUpButton />
              {/* <GoogleOneTap /> */}
            </SignedOut>
            <SignedIn>
              <UserButton />
            </SignedIn>
          </header>
          <ThemeProvider>
            <Navbar />
            {children}
          </ThemeProvider>
        </body>
        
        {/* <body className="bg-white text-black dark:bg-gray-900 dark:text-white">
          <ThemeProvider>
            <Navbar />
            {children}
          </ThemeProvider>
        </body> */}
      </html>
    </ClerkProvider>
  );
}
