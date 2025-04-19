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
import { Inter, Geist_Mono } from 'next/font/google'

import type { AppProps } from "next/app";

import ThemeProvider from "@components/ThemeProvider";
import { type Metadata } from "next";
import Navbar from "@components/Navbar";
import Welcome from "./components/Welcome";
import SignedOutNav from "./components/SignedOutNav";

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
  display: 'swap',
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
      <body className={`${inter.variable} ${geistMono.variable} font-sans antialiased dark:bg-gray-800`}>
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
              <div className="flex justify-center items-center h-[80vh] dark:bg-gray-700">
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
