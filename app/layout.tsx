import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import type React from "react";
import { Toaster } from "@/components/ui/toaster";
import { RouteLoader } from "@/components/route-loader";
import ClientEnergySyncWrapper from "@/app/components/client-energy-sync-wrapper";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Smart Home Dashboard | Sync",
  description: "Modern smart home control and monitoring system",
  generator: "Sync Studios",
  applicationName: "Sync Smart Home",
  keywords: ["smart home", "home automation", "energy monitoring", "IoT"],
  authors: [{ name: "Sync Development Team" }],
  viewport: "width=device-width, initial-scale=1",
  themeColor: "#FF9500",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        {/* Preload key assets to improve initial load performance */}
        <link rel="preload" href="/Login1.png" as="image" />
      </head>
      <body className={inter.className}>
        {/* Route loading indicator for navigation transitions */}
        <RouteLoader />
        <ClientEnergySyncWrapper>
          {children}
        </ClientEnergySyncWrapper>
        <Toaster />
      </body>
    </html>
  );
}