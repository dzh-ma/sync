"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Battery, ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Room {
  id: string
  name: string
  consumption: number
}

interface RoomEnergyConsumptionProps {
  rooms: Room[]
}

export function RoomEnergyConsumption({ rooms }: RoomEnergyConsumptionProps) {
  const [currentRoomIndex, setCurrentRoomIndex] = useState(0)

  const currentRoom = rooms[currentRoomIndex]

  const handlePrevRoom = () => {
    setCurrentRoomIndex((prevIndex) => (prevIndex > 0 ? prevIndex - 1 : rooms.length - 1))
  }

  const handleNextRoom = () => {
    setCurrentRoomIndex((prevIndex) => (prevIndex < rooms.length - 1 ? prevIndex + 1 : 0))
  }

  const getConsumptionColor = (consumption: number) => {
    if (consumption < 20) return "bg-green-500"
    if (consumption < 50) return "bg-yellow-500"
    return "bg-red-500"
  }

  return (
    <Card className="col-span-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Room Energy Consumption</CardTitle>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="icon" onClick={handlePrevRoom}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button variant="outline" size="icon" onClick={handleNextRoom}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Battery className="h-8 w-8 text-[#00B2FF]" />
            <div>
              <h3 className="text-lg font-semibold">{currentRoom.name}</h3>
              <p className="text-sm text-gray-500">Current consumption</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold">{currentRoom.consumption} kWh</p>
            <p className="text-sm text-gray-500">Today's usage</p>
          </div>
        </div>
        <div className="mt-4">
          <div className="h-4 w-full bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full ${getConsumptionColor(currentRoom.consumption)}`}
              style={{ width: `${Math.min((currentRoom.consumption / 100) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
        <div className="mt-2 flex justify-between text-sm text-gray-500">
          <span>0 kWh</span>
          <span>50 kWh</span>
          <span>100 kWh</span>
        </div>
      </CardContent>
    </Card>
  )
}

