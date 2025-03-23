"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Clock } from "lucide-react"

export function TimeDateWidget() {
  const [currentTime, setCurrentTime] = useState<Date | null>(null)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    // Mark component as mounted (client-side only)
    setMounted(true)
    setCurrentTime(new Date())
    
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
  }

  // Only render time content when mounted (client-side)
  const timeContent = mounted && currentTime ? (
    <>
      <div className="text-2xl font-bold">{formatTime(currentTime)}</div>
      <p className="text-xs text-muted-foreground">{formatDate(currentTime)}</p>
    </>
  ) : (
    <>
      <div className="text-2xl font-bold">Loading...</div>
      <p className="text-xs text-muted-foreground">Loading date...</p>
    </>
  )

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Current Time & Date</CardTitle>
        <Clock className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {timeContent}
      </CardContent>
    </Card>
  )
}

