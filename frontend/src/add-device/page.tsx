"use client"

import React from "react"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card"
import { Button } from "../../components/ui/button"
import { Input } from "../../components/ui/input"
import { Label } from "../../components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select"
import {
  Lightbulb,
  Thermometer,
  Fan,
  Tv,
  Lock,
  Plus,
  Plug,
  Coffee,
  Microwave,
  FolderIcon as Fridge,
  WashingMachine,
  ArrowLeft,
} from "lucide-react"
import { motion } from "framer-motion"
import { useNavigate } from "react-router-dom"

const deviceTypes = [
  { value: "light", label: "Light", icon: Lightbulb },
  { value: "thermostat", label: "Thermostat", icon: Thermometer },
  { value: "fan", label: "Fan", icon: Fan },
  { value: "tv", label: "TV", icon: Tv },
  { value: "lock", label: "Smart Lock", icon: Lock },
  { value: "plug", label: "Smart Plug", icon: Plug },
  { value: "coffee_maker", label: "Coffee Maker", icon: Coffee },
  { value: "microwave", label: "Microwave", icon: Microwave },
  { value: "refrigerator", label: "Refrigerator", icon: Fridge },
  { value: "washing_machine", label: "Washing Machine", icon: WashingMachine },
]

export default function AddDevicePage() {
  const navigate = useNavigate()
  const [deviceName, setDeviceName] = useState("")
  const [deviceType, setDeviceType] = useState("")
  const [room, setRoom] = useState("")

  const handleAddDevice = (e: React.FormEvent) => {
    e.preventDefault()

    const newDevice = {
      id: Date.now().toString(),
      name: deviceName,
      type: deviceType,
      room: room,
      status: "off",
      powerConsumption: getDevicePowerConsumption(deviceType),
      lastStatusChange: Date.now(),
      totalEnergyConsumed: 0,
    }

    const existingDevices = JSON.parse(localStorage.getItem("devices") || "[]")
    const updatedDevices = [...existingDevices, newDevice]
    localStorage.setItem("devices", JSON.stringify(updatedDevices))

    navigate("/devices")
  }

  const getDevicePowerConsumption = (deviceType: string): number => {
    const consumptionMap: { [key: string]: number } = {
      light: 10,
      thermostat: 50,
      fan: 60,
      tv: 100,
      refrigerator: 150,
      washing_machine: 500,
      microwave: 1000,
    }
    return consumptionMap[deviceType] || 50
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <header className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-6 w-6" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Add New Device</h1>
            <p className="text-sm text-gray-500">Connect a new smart device to your home</p>
          </div>
        </div>
      </header>

      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle className="text-[#00B2FF]">Device Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAddDevice} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name">Device Name</Label>
              <Input
                id="name"
                value={deviceName}
                onChange={(e) => setDeviceName(e.target.value)}
                placeholder="Enter device name"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="type">Device Type</Label>
              <Select value={deviceType} onValueChange={setDeviceType} required>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select device type" />
                </SelectTrigger>
                <SelectContent>
                  {deviceTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      <div className="flex items-center">
                        <type.icon className="mr-2 h-4 w-4 text-[#00B2FF]" />
                        {type.label}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="room">Room</Label>
              <Select value={room} onValueChange={setRoom} required>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select room" />
                </SelectTrigger>
                <SelectContent>
                  {JSON.parse(localStorage.getItem("rooms") || "[]").map((room: any) => (
                    <SelectItem key={room.id} value={room.name}>
                      {room.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex gap-4">
              <Button type="button" variant="outline" className="flex-1" onClick={() => navigate(-1)}>
                Cancel
              </Button>
              <Button type="submit" className="flex-1 bg-[#00B2FF] hover:bg-[#00B2FF]/90">
                <Plus className="mr-2 h-4 w-4" /> Add Device
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-8 max-w-2xl mx-auto"
      >
        <h2 className="text-xl font-semibold mb-4">Compatible Devices</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {deviceTypes.map((type) => (
            <Card
              key={type.value}
              className="flex flex-col items-center p-4 cursor-pointer hover:shadow-md transition-shadow"
            >
              <type.icon className="h-8 w-8 text-[#00B2FF] mb-2" />
              <p className="text-sm text-center">{type.label}</p>
            </Card>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

