"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Battery, Home } from "lucide-react"
import { Progress } from "@/components/ui/progress"

interface Device {
  id: string
  name: string
  type: string
  room: string
  status: "on" | "off"
}

interface Room {
  id: string
  name: string
  image?: string
}

interface RoomConsumptionWidgetProps {
  rooms: Room[]
  devices: Device[]
  calculateRoomEnergy: (roomName: string) => number
}

export function RoomConsumptionWidget({ rooms, devices, calculateRoomEnergy }: RoomConsumptionWidgetProps) {
  // Skip rendering if no rooms or devices
  if (rooms.length === 0 || devices.length === 0) {
    return null
  }

  // Calculate total energy consumption
  const totalEnergy = rooms.reduce((total, room) => {
    return total + calculateRoomEnergy(room.name)
  }, 0)

  // Get consumption color based on value
  const getConsumptionColor = (consumption: number) => {
    if (consumption < 2) return "bg-green-500"
    if (consumption < 5) return "bg-yellow-500"
    return "bg-red-500"
  }

  // Calculate percentage of total for each room
  const roomsWithConsumption = rooms
    .map((room) => {
      const consumption = calculateRoomEnergy(room.name)
      const percentage = totalEnergy > 0 ? (consumption / totalEnergy) * 100 : 0
      const deviceCount = devices.filter((d) => d.room === room.name).length
      const activeDevices = devices.filter((d) => d.room === room.name && d.status === "on").length

      return {
        ...room,
        consumption,
        percentage,
        deviceCount,
        activeDevices,
      }
    })
    .sort((a, b) => b.consumption - a.consumption) // Sort by consumption (highest first)

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-xl">
          <Battery className="h-5 w-5 text-[#00B2FF]" />
          Room Energy Consumption
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {roomsWithConsumption.map((room) => (
            <div key={room.id} className="space-y-2">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <Home className="h-4 w-4 text-gray-500" />
                  <span className="font-medium">{room.name}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs text-gray-500 whitespace-nowrap">
                    {room.activeDevices}/{room.deviceCount} devices active
                  </span>
                  <span className="font-semibold text-[#00B2FF] min-w-[70px] text-right">
                    {room.consumption.toFixed(1)} kWh
                  </span>
                </div>
              </div>
              <div className="relative pt-1 w-full">
                <Progress
                  value={room.percentage}
                  className="h-2 w-full"
                  indicatorClassName={getConsumptionColor(room.consumption)}
                />
              </div>
            </div>
          ))}

          <div className="flex justify-between items-center pt-4 border-t mt-4">
            <span className="font-medium">Total Consumption</span>
            <span className="font-bold text-[#00B2FF] min-w-[70px] text-right">{totalEnergy.toFixed(1)} kWh</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

