"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { ChevronRight } from "lucide-react"

interface RoomSelectorProps {
  selectedRoom: string
  onSelectRoom: (room: string) => void
}

export function RoomSelector({ selectedRoom, onSelectRoom }: RoomSelectorProps) {
  const [rooms, setRooms] = useState(["Living Room", "Bedroom", "Kitchen", "Bathroom", "Office", "Kids Room"])

  useEffect(() => {
    const storedRooms = JSON.parse(localStorage.getItem("rooms") || "[]")
    if (storedRooms.length > 0) {
      setRooms((prevRooms) => [...prevRooms, ...storedRooms.map((room: any) => room.name)])
    }
  }, [])

  return (
    <div className="flex items-center space-x-2 overflow-x-auto py-2">
      {rooms.map((room) => (
        <Button
          key={room}
          variant={room === selectedRoom ? "default" : "ghost"}
          className={room === selectedRoom ? "bg-[#00B2FF] hover:bg-[#00B2FF]/90" : ""}
          onClick={() => onSelectRoom(room)}
        >
          {room}
        </Button>
      ))}
      <Button variant="ghost" size="icon">
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  )
}

