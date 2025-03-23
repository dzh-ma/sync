"use client"

import { useEffect, useState } from "react"
import { Bell } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/components/ui/use-toast"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export function SuggestionNotification() {
  const [hasNewSuggestions, setHasNewSuggestions] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    const checkForSuggestions = async () => {
      try {
        // Get devices from localStorage
        const storedDevices = localStorage.getItem("devices")
        const devices = storedDevices ? JSON.parse(storedDevices) : []

        // Skip API call if no devices
        if (devices.length === 0) return

        // Get previously stored suggestions
        const storedSuggestions = localStorage.getItem("suggestions")
        const previousSuggestions = storedSuggestions ? JSON.parse(storedSuggestions) : []

        // Call the suggestions API
        const response = await fetch("/api/suggestions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            devices,
            previousSuggestions,
          }),
        })

        if (!response.ok) {
          throw new Error("Failed to fetch suggestions")
        }

        const data = await response.json()

        // Update state based on API response
        setHasNewSuggestions(data.hasNewSuggestions || false)

        // Store the current suggestions
        localStorage.setItem("suggestions", JSON.stringify(data.suggestions || []))

        // Show notification for new suggestions
        if (data.hasNewSuggestions) {
          toast({
            title: "New Energy Saving Suggestions",
            description: "We've identified new ways to optimize your energy usage.",
            action: (
              <Link href="/suggestions">
                <Button variant="outline" size="sm">
                  View
                </Button>
              </Link>
            ),
          })
        }
      } catch (err) {
        console.error("Error checking for suggestions:", err)
      }
    }

    // Check immediately on component mount
    checkForSuggestions()

    // Set up polling for new suggestions every 5 minutes
    const pollInterval = setInterval(checkForSuggestions, 5 * 60 * 1000)

    return () => clearInterval(pollInterval)
  }, [toast])

  if (!hasNewSuggestions) return null

  return (
    <Link href="/suggestions">
      <Badge variant="destructive" className="animate-pulse cursor-pointer">
        <Bell className="h-3 w-3 mr-1" /> New Suggestions
      </Badge>
    </Link>
  )
}

