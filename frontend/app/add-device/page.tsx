// app/add-device/page.tsx
"use client"

import React, { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useToast } from "@/components/ui/use-toast"
import {
  Lightbulb,
  Thermometer,
  Lock,
  Camera,
  Activity as Sensor,
  Switch,
  Plug,
  Speaker,
  HelpCircle,
  Plus,
  ArrowLeft,
} from "lucide-react"
import { motion } from "framer-motion"

// Match the DeviceType enum from the backend
const deviceTypes = [
  { value: "light", label: "Light", icon: Lightbulb },
  { value: "thermostat", label: "Thermostat", icon: Thermometer },
  { value: "lock", label: "Lock", icon: Lock },
  { value: "camera", label: "Camera", icon: Camera },
  { value: "sensor", label: "Sensor", icon: Sensor },
  { value: "switch", label: "Switch", icon: Switch },
  { value: "outlet", label: "Outlet", icon: Plug },
  { value: "speaker", label: "Speaker", icon: Speaker },
  { value: "other", label: "Other", icon: HelpCircle },
]

// Interface for Room from API
interface Room {
  id: string;
  name: string;
  home_id: string;
  type: string;
  floor: number;
  devices: string[];
  created: string;
}

export default function AddDevicePage() {
  const router = useRouter()
  const { toast } = useToast()
  
  // Form state
  const [deviceName, setDeviceName] = useState("")
  const [deviceType, setDeviceType] = useState("")
  const [roomId, setRoomId] = useState("")
  const [manufacturer, setManufacturer] = useState("")
  const [model, setModel] = useState("")
  const [ipAddress, setIpAddress] = useState("")
  const [macAddress, setMacAddress] = useState("")
  
  // API data
  const [rooms, setRooms] = useState<Room[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [userId, setUserId] = useState<string>("")

  // Fetch current user info and rooms on component mount
  useEffect(() => {
    const fetchUserAndRooms = async () => {
      try {
        // Fetch current user (in a real app, this would likely come from an auth context)
        const userResponse = await fetch('/api/v1/users/current')
        if (!userResponse.ok) throw new Error('Failed to fetch user data')
        const userData = await userResponse.json()
        setUserId(userData.id)

        // Fetch rooms
        const roomsResponse = await fetch('/api/v1/rooms')
        if (!roomsResponse.ok) throw new Error('Failed to fetch rooms')
        const roomsData = await roomsResponse.json()
        setRooms(roomsData)
      } catch (error) {
        console.error('Error fetching initial data:', error)
        toast({
          title: "Error",
          description: "Failed to load initial data. Please refresh the page.",
          variant: "destructive",
        })
      }
    }

    fetchUserAndRooms()
  }, [toast])

  const handleAddDevice = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!userId) {
      toast({
        title: "Error",
        description: "User authentication error. Please log in again.",
        variant: "destructive",
      })
      return
    }

    if (!deviceName || !deviceType) {
      toast({
        title: "Error",
        description: "Device name and type are required.",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)

    try {
      // Prepare the device data according to the CreateDevice model
      const deviceData = {
        name: deviceName,
        type: deviceType,
        user_id: userId,
        room_id: roomId || undefined,
        ip_address: ipAddress || undefined,
        mac_address: macAddress || undefined,
        manufacturer: manufacturer || undefined,
        model: model || undefined,
      }

      // Send device creation request to the API
      const response = await fetch('/api/v1/devices', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deviceData),
        credentials: 'include', // Include credentials for authentication
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to add device')
      }

      // Success! Show toast and redirect
      toast({
        title: "Success",
        description: "Device added successfully!",
      })

      router.push("/devices")
    } catch (error) {
      console.error("Failed to add device:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to add device. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <header className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="h-6 w-6" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Add New Device</h1>
            <p className="text-sm text-gray-500">Connect a new smart device to your Sync home</p>
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
              <Label htmlFor="name">Device Name *</Label>
              <Input
                id="name"
                value={deviceName}
                onChange={(e) => setDeviceName(e.target.value)}
                placeholder="Enter device name"
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="type">Device Type *</Label>
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
              <Label htmlFor="room">Room (Optional)</Label>
              <Select value={roomId} onValueChange={setRoomId}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select room" />
                </SelectTrigger>
                <SelectContent>
                  {rooms.map((room) => (
                    <SelectItem key={room.id} value={room.id}>
                      {room.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="manufacturer">Manufacturer (Optional)</Label>
                <Input
                  id="manufacturer"
                  value={manufacturer}
                  onChange={(e) => setManufacturer(e.target.value)}
                  placeholder="e.g., Philips, Samsung"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="model">Model (Optional)</Label>
                <Input
                  id="model"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  placeholder="e.g., Hue Bulb, WF450"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="ipAddress">IP Address (Optional)</Label>
                <Input
                  id="ipAddress"
                  value={ipAddress}
                  onChange={(e) => setIpAddress(e.target.value)}
                  placeholder="e.g., 192.168.1.100"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="macAddress">MAC Address (Optional)</Label>
                <Input
                  id="macAddress"
                  value={macAddress}
                  onChange={(e) => setMacAddress(e.target.value)}
                  placeholder="e.g., AA:BB:CC:DD:EE:FF"
                />
              </div>
            </div>
            
            <div className="flex gap-4 pt-2">
              <Button 
                type="button" 
                variant="outline" 
                className="flex-1" 
                onClick={() => router.back()}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                className="flex-1 bg-[#00B2FF] hover:bg-[#00B2FF]/90"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Adding...
                  </span>
                ) : (
                  <>
                    <Plus className="mr-2 h-4 w-4" /> Add Device
                  </>
                )}
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
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
          {deviceTypes.map((type) => (
            <Card
              key={type.value}
              className={`flex flex-col items-center p-4 cursor-pointer hover:shadow-md transition-all ${
                deviceType === type.value ? "ring-2 ring-[#00B2FF] bg-blue-50" : ""
              }`}
              onClick={() => setDeviceType(type.value)}
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
