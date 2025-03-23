"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import {
    Lightbulb,
    Thermometer,
    Fan,
    Tv,
    Lock,
  ArrowLeft,
    Plus,
    Plug,
    Coffee,
    Microwave,
    FolderIcon as Fridge,
    WashingMachine,
} from "lucide-react"
import { motion } from "framer-motion"
import { toast } from "@/components/ui/use-toast"
import { NavigationSidebar } from "@/app/components/navigation-sidebar"
import axios from "axios"
import { v4 as uuidv4 } from "uuid"

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Room {
  id: string
  name: string
  type: string
  image?: string
}

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

const POWER_CONSUMPTION_RANGES = {
  "light": [5, 15],           // LED Light Bulb
  "thermostat": [1, 5],       // Smart Thermostat
  "fan": [10, 75],            // Ceiling Fan
  "tv": [40, 250],            // TV
  "lock": [0.1, 2],           // Smart Lock
  "plug": [1, 3],             // Smart Plug
  "coffee_maker": [600, 1200], // Coffee Maker
  "microwave": [600, 1500],   // Microwave
  "refrigerator": [100, 800], // Refrigerator
  "washing_machine": [500, 2000], // Washing Machine
};

const generateRandomPowerConsumption = (deviceType: string): number => {
  // Convert deviceType to lowercase to match keys
  const deviceTypeLower = deviceType.toLowerCase();
  
  // Get the range for this device type, or use a default
  const range = POWER_CONSUMPTION_RANGES[deviceTypeLower as keyof typeof POWER_CONSUMPTION_RANGES] || [1, 10];
  const [min, max] = range;
  
  // Generate a random value within the range
  const randomValue = Math.random() * (max - min) + min;
  
  // Log for debugging
  console.log(`Generating power for ${deviceType}: range ${min}-${max}, value: ${randomValue.toFixed(1)}`);
  
  return parseFloat(randomValue.toFixed(1));
};

export default function AddDevicePage() {
    const router = useRouter()
    const [deviceName, setDeviceName] = useState("")
    const [deviceType, setDeviceType] = useState("")
    const [room, setRoom] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [rooms, setRooms] = useState<Room[]>([])
  const [isLoadingRooms, setIsLoadingRooms] = useState(true)

    useEffect(() => {
    fetchRooms()
  }, [])

    const fetchRooms = async () => {
    setIsLoadingRooms(true)
    try {
      // Check for both currentUser (admin) and currentMember (household member)
      const storedUser = localStorage.getItem("currentUser")
      const storedMember = localStorage.getItem("currentMember")
      
      let userId, householdId
      
      if (storedUser) {
        const currentUser = JSON.parse(storedUser)
        userId = currentUser.id
        householdId = currentUser.householdId
        console.log("Using currentUser:", { userId, householdId })
      } else if (storedMember) {
        const currentMember = JSON.parse(storedMember)
        userId = currentMember.id
        householdId = currentMember.householdId
        console.log("Using currentMember:", { userId, householdId })
      }
            
      if (!householdId) {
        console.error("No householdId found in user data")
        toast({
          title: "Error",
          description: "Household ID not found. Please login again.",
          variant: "destructive",
        })
        
        setRooms([])
        setIsLoadingRooms(false)
        return
      }
      
      console.log("Fetching rooms with household ID:", householdId)
      
      // Try to fetch rooms from the API
      try {
        console.log(`Fetching rooms from API: ${API_URL}/api/rooms?household_id=${householdId}`)
        const response = await axios.get(`${API_URL}/api/rooms`, {
          params: { household_id: householdId },
          timeout: 8000
        })
        
        if (response.data && Array.isArray(response.data)) {
          if (response.data.length > 0) {
            console.log("Found rooms:", response.data)
            
            // Format the room data
            const formattedRooms = response.data.map((room: any) => ({
              id: room.id || room._id || uuidv4(),
              name: room.name || room.room_name || "Unknown Room",
              type: room.type || room.room_type || "unknown",
              image: room.image
            }))
            
            console.log("Formatted rooms:", formattedRooms)
            
            // Save rooms to localStorage for future reference
            localStorage.setItem("rooms", JSON.stringify(formattedRooms))
            
            setRooms(formattedRooms)
            setIsLoadingRooms(false)
            return
          } else {
            console.log("API returned empty room array")
            setRooms([])
          }
        } else {
          console.log("API response is not a room array:", response.data)
          setRooms([])
        }
      } catch (error) {
        console.error("API request for rooms failed:", error)
        
        // On API failure, try to use cached rooms from localStorage as fallback
        const storedRooms = JSON.parse(localStorage.getItem("rooms") || "[]")
        
        if (Array.isArray(storedRooms) && storedRooms.length > 0) {
          console.log("Using cached rooms from localStorage:", storedRooms)
          setRooms(storedRooms)
        } else {
          console.log("No rooms found in localStorage either")
          setRooms([])
        }
      }
    } catch (error) {
      console.error("Error fetching rooms:", error)
      setRooms([])
    } finally {
      setIsLoadingRooms(false)
    }
  }

    const handleAddDevice = async (e: React.FormEvent) => {
        e.preventDefault()
        
        // First, validate that a room is selected if rooms are available
        if (rooms.length > 0 && !room) {
          toast({
            title: "Error",
            description: "Please select a room for the device.",
            variant: "destructive",
          })
          return
        }
        
        setIsLoading(true)
        try {
          // Check for both currentUser (admin) and currentMember (household member)
          const storedUser = localStorage.getItem("currentUser")
          const storedMember = localStorage.getItem("currentMember")
          
          let userId, householdId
          
          if (storedUser) {
            const currentUser = JSON.parse(storedUser)
            userId = currentUser.id
            householdId = currentUser.householdId
          } else if (storedMember) {
            const currentMember = JSON.parse(storedMember)
            userId = currentMember.id
            householdId = currentMember.householdId
          }

                // Validate user information
          if (!userId || !householdId) {
                    toast({
                        title: "Error",
                        description: "User or Household ID not found. Please log in again.",
                        variant: "destructive",
            })
            return
                }

                // Generate random power consumption based on device type
                const basePowerConsumption = generateRandomPowerConsumption(deviceType)

                const newDevice = {
                    user_id: userId,
                    device_name: deviceName,
                    deviceType: deviceType,
                    room: room || "",  // Use empty string if room is not selected
                    household_id: householdId,
                    status: "off",
                    base_power_consumption: basePowerConsumption,
                    power_consumption: 0,
                    total_energy_consumed: 0,
                    lastStatusChange: Date.now(),
                    settings: {
                        brightness: deviceType === "light" ? 80 : null,
                        temperature: deviceType === "thermostat" ? 22 : null,
                        speed: deviceType === "fan" ? 2 : null,
                    }
                }
                console.log("Sending:", newDevice)

          const response = await fetch(`${API_URL}/api/user/add-device`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(newDevice),
          })

                if (!response.ok) {
                    // Read the response body as text
            const errorText = await response.text()
            console.error("Full backend error:", errorText)

                    // Try to parse the error as JSON; if it fails, use the raw text
            let errorMessage = "Failed to add device"
            try {
              const errorData = JSON.parse(errorText)
              if (typeof errorData === 'object' && errorData !== null) {
                errorMessage = errorData.detail?.message || 
                              (typeof errorData.detail === 'string' ? errorData.detail : errorMessage)
              }
            } catch (e) {
              errorMessage = errorText || errorMessage
            }

            toast({
              title: "Error",
              description: errorMessage,
              variant: "destructive",
            })
            return
          }

          // Get the response data if available
          let responseData
          try {
            responseData = await response.json()
            console.log("Add device response:", responseData)
          } catch (e) {
            console.log("No JSON response from add-device")
          }

          // Create a device object for local storage
          const localDevice = {
            id: responseData?.id || `${deviceType}-${Date.now()}`,
            name: deviceName,
            type: deviceType,
            room: room || "",  // Use empty string if room is not selected
            status: "off",
            basePowerConsumption: basePowerConsumption,
            powerConsumption: 0,
            totalEnergyConsumed: 0,
            lastStatusChange: Date.now(),
            brightness: deviceType === "light" ? 80 : undefined,
            temperature: deviceType === "thermostat" ? 22 : undefined,
            speed: deviceType === "fan" ? 2 : undefined,
          }

          // Also log the basePowerConsumption for debugging
          console.log(`Generated power consumption for ${deviceType}: ${basePowerConsumption} W`);

          // Update localStorage with the new device
          const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]")
          const updatedDevices = [...storedDevices, localDevice]
          localStorage.setItem("devices", JSON.stringify(updatedDevices))

          console.log("Device added to localStorage:", localDevice)
          console.log("Updated devices in localStorage:", updatedDevices)

                toast({
                    title: "Success",
                    description: "Device added successfully!",
          })
          
          // Navigate to devices page after a short delay to allow localStorage to update
          setTimeout(() => {
            router.push("/devices")
          }, 500)

            } catch (error: any) {
          console.error("Error adding device:", error)
                toast({
                    title: "Error",
                    description: error.message || "Failed to add device",
                    variant: "destructive",
          })
            } finally {
          setIsLoading(false)
        }
            }

    return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex">
      <NavigationSidebar />
      <div className="flex-1 ml-[72px] p-6">
            <header className="flex items-center mb-8">
                <Button variant="ghost" size="icon" onClick={() => router.back()}>
                    <ArrowLeft className="h-6 w-6" />
                </Button>
                <div>
                    <h1 className="text-2xl font-bold text-gray-800">Add New Device</h1>
                    <p className="text-sm text-gray-500">Connect a new smart device to your home</p>
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
                            {isLoadingRooms ? (
                              <div className="flex items-center justify-center p-6 border rounded-lg">
                                <div className="w-6 h-6 border-2 border-t-[#00B2FF] border-[#FF9500]/20 rounded-full animate-spin mr-2"></div>
                                <p className="text-sm text-gray-500">Loading rooms...</p>
                              </div>
                            ) : rooms.length > 0 ? (
                              <Select value={room} onValueChange={setRoom} required>
                                <SelectTrigger className="w-full">
                                  <SelectValue placeholder="Select a room" />
                                </SelectTrigger>
                                <SelectContent>
                                  {rooms.map((room) => (
                                    <SelectItem key={room.id} value={room.name}>
                                      {room.name}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            ) : (
                              <div className="flex flex-col items-center justify-center p-6 border border-dashed rounded-lg">
                                <p className="text-sm text-gray-500 mb-4">No rooms found. Please add a room first.</p>
                                <Button variant="outline" className="bg-white" onClick={() => router.push("/add-room")}>
                                  <Plus className="mr-2 h-4 w-4" /> Add Room
                                </Button>
                              </div>
                            )}
                        </div>
                        <div className="flex gap-4">
                            <Button type="button" variant="outline" className="flex-1" onClick={() => router.back()}>
                                Cancel
                            </Button>
                            <Button
                                type="submit"
                                className="flex-1 bg-[#70D0FF] hover:bg-[#70D0FF]/90"
                                disabled={isLoading || isLoadingRooms || rooms.length === 0}
                            >
                                <Plus className="mr-2 h-4 w-4" /> {isLoading ? "Adding..." : "Add Device"}
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
                className={`flex flex-col items-center p-4 cursor-pointer hover:shadow-md transition-shadow ${
                  deviceType === type.value ? "border-[#00B2FF] bg-blue-50" : ""
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
        </div>
    )
}

