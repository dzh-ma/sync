"use client"

import type React from "react"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Home,
  Smartphone,
  Plus,
  ArrowRight,
  Zap,
  Clock,
  Lightbulb,
  ChevronRight,
  Fan,
  Tv,
  FileText,
  Info,
  HelpCircle,
  Leaf,
  BarChart2,
  Wifi,
  Thermometer,
  Move,
  Check,
  X,
} from "lucide-react"
import { motion } from "framer-motion"
import Link from "next/link"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import Image from "next/image"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { EnergyUsageWidget } from "@/app/components/energy-usage-widget"
import { WeatherEnergyWidget } from "@/app/components/weather-energy-widget"
import { SortableWidget } from "@/app/components/sortable-widget"
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from "@dnd-kit/core"
import { SortableContext, arrayMove, rectSortingStrategy } from "@dnd-kit/sortable"
import { restrictToParentElement } from "@dnd-kit/modifiers"
import { VoiceAssistant } from "@/app/components/voice-assistant"
import { RoomConsumptionWidget } from "@/app/components/room-consumption-widget"
import { NavigationSidebar } from "@/app/components/navigation-sidebar"
import axios, { AxiosError } from "axios"
import { toast } from "@/components/ui/use-toast"

// API URL for backend
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// Remove the import for QuickActionsWidget
interface Room {
  id: string
  name: string
  image?: string
}

interface Device {
  id: string
  name: string
  type: string
  room: string
  status: "on" | "off"
  lastStatusChange?: number
  basePowerConsumption?: number
  totalEnergyConsumed?: number
}

interface Automation {
  id: number
  name: string
  description: string
  icon: string
  active: boolean
  schedule: {
    type: string
    startTime: string
    endTime: string
  }
}

// Update the Suggestion interface in your dashboard page
interface Suggestion {
  title: string
  description: string
  icon?: any
  iconColor: string
  saving: string
  impact?: string
  action?: string
  category?: string
  details?: string[]
}

// Define a Widget interface for the dashboard
interface Widget {
  id: string
  type: string
  content: React.ReactNode
}

// Define interface for API suggestion response
interface APISuggestion {
  title: string
  description: string
  icon: string
  iconColor: string
  saving: string
  impact?: string
  action?: string
  category?: string
  details?: string[]
}

const getAutomationIcon = (icon: string) => {
  switch (icon) {
    case "light":
      return <Lightbulb className="h-4 w-4 text-yellow-500" />
    case "thermostat":
      return <Zap className="h-4 w-4 text-red-500" />
    case "fan":
      return <Zap className="h-4 w-4 text-blue-500" />
    default:
      return <Smartphone className="h-4 w-4 text-gray-500" />
  }
}

const generateDeviceSpecificTips = (devices: Device[]) => {
  const tips: Suggestion[] = []

  // Group devices by type
  const devicesByType = devices.reduce(
    (acc, device) => {
      acc[device.type] = [...(acc[device.type] || []), device]
      return acc
    },
    {} as Record<string, Device[]>,
  )

  // Generate tips based on device types and states
  if (devicesByType["thermostat"]) {
    const activeThermostats = devicesByType["thermostat"].filter((d) => d.status === "on")
    if (activeThermostats.length > 0) {
      tips.push({
        title: "Optimize Air Conditioning",
        description: "Your AC has been running continuously. Consider setting up a schedule.",
        icon: Fan,
        iconColor: "text-blue-500",
        saving: "Potential saving: 120 kWh/month",
      })
    }
  }

  if (devicesByType["light"]) {
    const activeLights = devicesByType["light"].filter((d) => d.status === "on")
    if (activeLights.length > 2) {
      tips.push({
        title: "Smart Lighting Pattern",
        description: "Multiple lights are on. Consider automation for better efficiency.",
        icon: Lightbulb,
        iconColor: "text-yellow-500",
        saving: "Potential saving: 45 kWh/month",
      })
    }
  }

  if (devicesByType["tv"]) {
    tips.push({
      title: "Standby Power Usage",
      description: "Enable auto-shutdown for your TV to save energy when not in use.",
      icon: Tv,
      iconColor: "text-purple-500",
      saving: "Potential saving: 30 kWh/month",
    })
  }

  // Add general tips if there are any devices
  if (devices.length > 0) {
    tips.push({
      title: "Off-Peak Usage",
      description: "Schedule your devices during off-peak hours for better rates.",
      icon: Clock,
      iconColor: "text-green-500",
      saving: "Potential saving: 80 kWh/month",
    })
  }

  return tips
}

const calculateEnergyData = (devices: Device[]) => {
  const data = []
  const now = new Date()

  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)

    // Calculate actual usage based on active devices
    const activeDevices = devices.filter((d) => d.status === "on")
    const baseUsage = activeDevices.length * 2 // Base usage per device
    const timeVariation = Math.sin((date.getHours() / 24) * Math.PI * 2) * activeDevices.length // Daily pattern
    const randomVariation = Math.random() * activeDevices.length // Random variation
    const usage = Math.max(0, baseUsage + timeVariation + randomVariation)

    data.push({
      name: date.toLocaleDateString("en-US", { weekday: "short" }),
      usage: Number(usage.toFixed(1)),
    })
  }

  return data
}

// Generate sample data for the energy usage widget
const generateSampleEnergyData = () => {
  const daily = Array.from({ length: 24 }, (_, i) => ({
    name: `${i}:00`,
    usage: Math.random() * 5 + 1,
  }))

  const weekly = Array.from({ length: 7 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - i)
    return {
      name: date.toLocaleDateString("en-US", { weekday: "short" }),
      usage: Math.random() * 30 + 10,
    }
  }).reverse()

  const monthly = Array.from({ length: 30 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - i)
    return {
      name: date.getDate().toString(),
      usage: Math.random() * 120 + 40,
    }
  }).reverse()

  return { daily, weekly, monthly }
}

export default function DashboardPage() {
  const [rooms, setRooms] = useState<Room[]>([])
  const [devices, setDevices] = useState<Device[]>([])
  const [automations, setAutomations] = useState<Automation[]>([])
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [loading, setLoading] = useState(true)
  const [energyData, setEnergyData] = useState<{ name: string; usage: number }[]>([])
  const [guideOpen, setGuideOpen] = useState(false)
  const [sampleEnergyData] = useState(generateSampleEnergyData())
  const [isEditing, setIsEditing] = useState(false)
  const [widgets, setWidgets] = useState<Widget[]>([])

  // Set up DnD sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor),
  )

  // Add this function inside your DashboardPage component
  // Update the fetchPythonSuggestions function to handle the new format
  const fetchSuggestions = useCallback(async () => {
    try {
      // Add lastStatusChange to devices if not present
      const devicesWithTimestamps = devices.map((device) => {
        if (!device.lastStatusChange) {
          // If device is on, set a random time in the past (1-8 hours)
          if (device.status === "on") {
            const hoursAgo = Math.floor(Math.random() * 8) + 1
            return {
              ...device,
              lastStatusChange: Date.now() - hoursAgo * 60 * 60 * 1000,
            }
          }
        }
        return device
      })

      const response = await fetch("/api/suggestions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ devices: devicesWithTimestamps }),
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`)
      }

      const data = await response.json()

      // Map the API suggestions to the format expected by the UI
      const formattedSuggestions = data.suggestions.map((suggestion: APISuggestion) => {
        // Map the icon string to the actual icon component
        let iconComponent
        switch (suggestion.icon) {
          case "Lightbulb":
            iconComponent = Lightbulb
            break
          case "Fan":
            iconComponent = Fan
            break
          case "Tv":
            iconComponent = Tv
            break
          case "Clock":
            iconComponent = Clock
            break
          case "Thermometer":
            iconComponent = Thermometer
            break
          case "BarChart2":
            iconComponent = BarChart2
            break
          default:
            iconComponent = Zap
        }

        return {
          ...suggestion,
          icon: iconComponent,
        }
      })

      setSuggestions(formattedSuggestions)
    } catch (error) {
      console.error("Failed to fetch suggestions:", error)
      // Fallback to client-side suggestions if API fails
      const newSuggestions = generateDeviceSpecificTips(devices)
      setSuggestions(newSuggestions)
    }
  }, [devices])

  // Initialize widgets
  useEffect(() => {
    // Log the current state to help debug
    console.log("Dashboard current state:", { 
      roomsCount: rooms.length, 
      devicesCount: devices.length 
    });
    
    if (rooms.length > 0 || devices.length > 0) {
      // Check if we have stored widget order
      const storedWidgets = localStorage.getItem("dashboardWidgets")

      if (storedWidgets) {
        try {
          const parsedWidgets = JSON.parse(storedWidgets)
          // Validate that the stored widgets match our expected structure
          if (Array.isArray(parsedWidgets) && parsedWidgets.length > 0 && parsedWidgets[0].id) {
            setWidgets(parsedWidgets)
            return
          }
        } catch (e) {
          console.error("Error parsing stored widgets:", e)
        }
      }

      // If no valid stored widgets, create default order
      initializeWidgets()
    }
  }, [rooms, devices, automations, suggestions])

  // Function to initialize widgets in default order
  const initializeWidgets = () => {
    const defaultWidgets: Widget[] = [
      {
        id: "energy-weather",
        type: "energy-weather",
        content: null, // Will be rendered dynamically
      },
      {
        id: "room-consumption",
        type: "room-consumption",
        content: null,
      },
      {
        id: "rooms",
        type: "rooms",
        content: null,
      },
      {
        id: "automations",
        type: "automations",
        content: null,
      },
      {
        id: "suggestions",
        type: "suggestions",
        content: null,
      },
      {
        id: "devices",
        type: "devices",
        content: null,
      },
    ]

    setWidgets(defaultWidgets)
  }

  // Replace the existing useEffect that sets suggestions with this:
  useEffect(() => {
    const newEnergyData = calculateEnergyData(devices)
    setEnergyData(newEnergyData)

    // Fetch suggestions
    fetchSuggestions()
  }, [devices, fetchSuggestions])

  // Load initial data
  useEffect(() => {
    const initializeData = async () => {
      try {
        setLoading(true)
        
        // Get user info from localStorage
        const storedUser = localStorage.getItem("currentUser")
        const storedMember = localStorage.getItem("currentMember")
        
        let userId: string | undefined
        let householdId: string | undefined
        
        if (storedUser) {
          const currentUser = JSON.parse(storedUser)
          userId = currentUser.id
          householdId = currentUser.householdId
        } else if (storedMember) {
          const currentMember = JSON.parse(storedMember)
          userId = currentMember.id
          householdId = currentMember.householdId
        }
        
        // Generate a default householdId if not found
        if (!householdId) {
          console.warn("Missing householdId. Using default value.")
          
          // Check if this user already has a generated householdId in localStorage
          const generatedHouseholdId = localStorage.getItem("generatedHouseholdId")
          
          if (generatedHouseholdId) {
            householdId = generatedHouseholdId
          } else {
            // Generate a random household ID for this session
            householdId = `default-household-${Date.now()}`
            localStorage.setItem("generatedHouseholdId", householdId)
          }
          
          // Update the user object with this generated householdId
          if (storedUser) {
            const currentUser = JSON.parse(storedUser)
            currentUser.householdId = householdId
            localStorage.setItem("currentUser", JSON.stringify(currentUser))
          } else if (storedMember) {
            const currentMember = JSON.parse(storedMember)
            currentMember.householdId = householdId
            localStorage.setItem("currentMember", JSON.stringify(currentMember))
          }
        }
        
        // For a fresh login, clear previous room and device data
        if (localStorage.getItem("freshLogin") === "true") {
          console.log("Fresh login detected, clearing previous data")
          localStorage.removeItem("rooms")
          localStorage.removeItem("devices")
          localStorage.removeItem("automations")
          localStorage.setItem("freshLogin", "false")
        }
        
        // Use localStorage data as fallback only if the same householdId
        let storedRooms: Room[] = []
        let storedDevices: Device[] = []
        let storedAutomations: Automation[] = []
        
        const roomsData = localStorage.getItem("rooms")
        const devicesData = localStorage.getItem("devices")
        const automationsData = localStorage.getItem("automations")
        
        if (roomsData) {
          const parsedRooms = JSON.parse(roomsData)
          // Only use stored rooms if there's a householdId match
          const storedHouseholdId = localStorage.getItem("currentHouseholdId")
          if (storedHouseholdId === householdId) {
            storedRooms = parsedRooms
          }
        }
        
        if (devicesData) {
          const parsedDevices = JSON.parse(devicesData)
          storedDevices = parsedDevices
        }
        
        if (automationsData) {
          const parsedAutomations = JSON.parse(automationsData)
          storedAutomations = parsedAutomations
        }
        
        // Store current householdId in localStorage for future reference
        localStorage.setItem("currentHouseholdId", householdId || '')
        
        // Set initial data from localStorage to prevent blank screens
        // Only use this as a temporary state before API data loads
        console.log("Setting initial data from localStorage:", {
          roomsCount: storedRooms.length,
          devicesCount: storedDevices.length
        });
        setRooms(storedRooms)
        setDevices(storedDevices)
        setAutomations(storedAutomations)
        
        // Track if we successfully loaded data from the backend
        let loadedFromBackend = false;
        
        if (userId || householdId) {
          console.log("Fetching data for user/household:", userId, householdId)
          
          try {
            // Fetch rooms from backend
            const roomsResponse = await axios.get(`${API_URL}/api/rooms`, {
              params: {
                household_id: householdId
              }
            })
            
            console.log("Rooms from backend:", roomsResponse.data)
            
            if (roomsResponse.data && Array.isArray(roomsResponse.data)) {
              // Format the rooms data if needed
              const backendRooms = roomsResponse.data.map(room => ({
                id: room.id || room._id,
                name: room.name,
                image: room.image
              }))
              
              // Update localStorage and state
              localStorage.setItem("rooms", JSON.stringify(backendRooms))
              setRooms(backendRooms)
              
              console.log("Updated rooms from backend:", backendRooms.length);
              loadedFromBackend = true;
            }
          } catch (error) {
            console.error("Error fetching rooms:", error)
            // Don't show old rooms if fetch fails - just empty the array
            const axiosError = error as AxiosError
            if (axiosError.response?.status === 422) {
              console.warn("Household ID may be missing or invalid. Clearing rooms data.")
              localStorage.setItem("rooms", JSON.stringify([]))
              setRooms([])
            }
          }
          
          try {
            // Fetch devices from backend
            const devicesResponse = await axios.get(`${API_URL}/api/user/devices`, {
              params: {
                user_id: userId,
                household_id: householdId
              }
            })
            
            console.log("Devices from backend:", devicesResponse.data)
            
            if (devicesResponse.data && Array.isArray(devicesResponse.data)) {
              // Create a map of existing devices for faster lookup
              const deviceMap = new Map()
              storedDevices.forEach((device: Device) => {
                deviceMap.set(device.name, device)
              })
              
              // Process devices from backend
              const backendDevices = devicesResponse.data.map(backendDevice => {
                const existingDevice = deviceMap.get(backendDevice.name)
                
                // Get power consumption from backend or generate a new one
                const basePowerConsumption = 
                  backendDevice.base_power_consumption || 
                  (existingDevice?.basePowerConsumption) || 
                  Math.random() * 5 + 0.5 // Random value between 0.5 and 5.5
                
                return {
                  id: backendDevice.id || backendDevice._id || `${backendDevice.type}-${Date.now()}`,
                  name: backendDevice.name,
                  type: backendDevice.type,
                  room: backendDevice.room,
                  status: backendDevice.status || "off",
                  basePowerConsumption: basePowerConsumption,
                  lastStatusChange: backendDevice.last_status_change || Date.now(),
                  // Preserve any other properties from existing device
                  ...(existingDevice || {})
                }
              })
              
              // Update localStorage and state
              localStorage.setItem("devices", JSON.stringify(backendDevices))
              setDevices(backendDevices)
              
              console.log("Updated devices from backend:", backendDevices.length);
              loadedFromBackend = true;
            }
          } catch (error) {
            console.error("Error fetching devices:", error)
            const axiosError = error as AxiosError
            if (axiosError.response?.status === 422) {
              console.warn("Household ID may be missing or invalid. Clearing devices data.")
              localStorage.setItem("devices", JSON.stringify([]))
              setDevices([])
            }
          }
          
          try {
            // Fetch automations from backend
            const automationsResponse = await axios.get(`${API_URL}/api/automations`, {
              params: {
                user_id: userId,
                household_id: householdId
              }
            })
            
            console.log("Automations from backend:", automationsResponse.data)
            
            if (automationsResponse.data && Array.isArray(automationsResponse.data)) {
              // Format the automations data
              const backendAutomations = automationsResponse.data.map(automation => ({
                id: automation.id || automation._id,
                name: automation.name,
                description: automation.description,
                icon: automation.icon,
                active: automation.active,
                schedule: automation.schedule
              }))
              
              // Update localStorage and state
              localStorage.setItem("automations", JSON.stringify(backendAutomations))
              setAutomations(backendAutomations)
            }
          } catch (error) {
            console.error("Error fetching automations:", error)
            // Keep showing old automations as fallback
          }
        }
        
        // Final console log after all data fetching is done
        console.log("Final data after initialization:", {
          roomsCount: rooms.length,
          devicesCount: devices.length,
          loadedFromBackend: loadedFromBackend
        });
        
      } catch (e) {
        console.error("Error initializing data:", e)
        toast({
          title: "Error",
          description: "Failed to load your smart home data. Please try again.",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }
    
    initializeData()
  }, [])

  const calculateRoomEnergy = (roomName: string): number => {
    const roomDevices = devices.filter((device) => device.room === roomName)
    const activeDevices = roomDevices.filter((device) => device.status === "on")
    return activeDevices.reduce((total, device) => {
      switch (device.type) {
        case "thermostat":
          return total + 5
        case "light":
          return total + 0.5
        case "tv":
          return total + 2
        default:
          return total + 1
      }
    }, 0)
  }

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case "light":
        return <Lightbulb className="h-4 w-4 text-yellow-500" />
      case "thermostat":
        return <Zap className="h-4 w-4 text-red-500" />
      case "fan":
        return <Fan className="h-4 w-4 text-blue-500" />
      case "tv":
        return <Tv className="h-4 w-4 text-purple-500" />
      default:
        return <Smartphone className="h-4 w-4 text-gray-500" />
    }
  }

  const toggleDevice = async (deviceId: string, isOn: boolean) => {
    try {
      // Find the device that will be toggled
      const deviceToToggle = devices.find(d => d.id === deviceId);
      if (!deviceToToggle) {
        console.error(`Device with ID ${deviceId} not found`);
        return;
      }
      
      // Get user info from localStorage
      const storedUser = localStorage.getItem("currentUser");
      const storedMember = localStorage.getItem("currentMember");
      
      let userId: string | undefined;
      let householdId: string | undefined;
      
      if (storedUser) {
        const currentUser = JSON.parse(storedUser);
        userId = currentUser.id;
        householdId = currentUser.householdId;
      } else if (storedMember) {
        const currentMember = JSON.parse(storedMember);
        userId = currentMember.id;
        householdId = currentMember.householdId;
      }

      if (!userId && !householdId) {
        console.error("No user ID or household ID found");
        toast({
          title: "Error",
          description: "User information not found. Please login again.",
          variant: "destructive",
        });
        return;
      }
      
      // Calculate energy consumed if turning off (when device was previously on)
      let energyConsumed = 0;
      if (deviceToToggle.status === "on" && !isOn && deviceToToggle.lastStatusChange) {
        const timeOn = (Date.now() - deviceToToggle.lastStatusChange) / 1000 / 3600; // hours
        energyConsumed = (deviceToToggle.basePowerConsumption || 0) * timeOn / 1000; // kWh
        console.log(`Device ${deviceToToggle.name} was on for ${timeOn.toFixed(2)} hours, consuming ${energyConsumed.toFixed(2)} kWh`);
        
        // First, trigger statistics collection BEFORE changing the device status
        // This ensures the current on-time is recorded properly in the statistics
        try {
          console.log("Triggering statistics collection before device toggle");
          const statsResponse = await fetch(`/api/statistics/collect`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              userId: userId || '',
              householdId: householdId || ''
            }),
          });
          
          if (statsResponse.ok) {
            console.log("Statistics collection triggered successfully before toggle");
          } else {
            console.warn("Failed to trigger statistics collection before toggle");
          }
        } catch (statsError) {
          console.error("Error triggering statistics collection:", statsError);
        }
      }

      // Update local state first for responsive UI
      const updatedDevices = devices.map((device) =>
        device.id === deviceId 
          ? { 
              ...device, 
              status: isOn ? "on" : "off" as "on" | "off", 
              lastStatusChange: Date.now(),
              totalEnergyConsumed: (device.totalEnergyConsumed || 0) + energyConsumed
            } 
          : device
      );
      
      setDevices(updatedDevices);
      
      // Get all devices from localStorage to avoid updating just the visible ones
      const allStoredDevices = JSON.parse(localStorage.getItem("devices") || "[]");
      
      // Update all devices in localStorage that match by id or name
      const updatedStoredDevices = allStoredDevices.map((device: any) => {
        if (device.id === deviceId || device.name === deviceToToggle.name) {
          return {
            ...device,
            status: isOn ? "on" : "off",
            lastStatusChange: Date.now(),
            totalEnergyConsumed: (device.totalEnergyConsumed || 0) + energyConsumed
          };
        }
        return device;
      });
      
      // Update localStorage with all updated devices
      localStorage.setItem("devices", JSON.stringify(updatedStoredDevices));
      
      // Sync with backend
      console.log(`Toggling device ${deviceToToggle.name} to ${isOn ? "on" : "off"}`);
      
      // Call backend API to update device status
      try {
        // Call backend API to update device status
        const response = await axios.put(`${API_URL}/api/user/toggle-device`, null, {
          params: {
            user_id: userId,
            device_name: deviceToToggle.name, // Backend uses device_name, not device_id
            household_id: householdId,
            status: isOn ? "on" : "off"
          }
        });
        
        console.log("Device toggle response:", response.data);
        
        // Toast notification for user feedback
        toast({
          title: `Device ${isOn ? "On" : "Off"}`,
          description: `${deviceToToggle.name} is now ${isOn ? "on" : "off"}.`,
        });
        
        // Now trigger statistics collection AFTER toggling the device
        // This ensures the new device state is recorded properly
        setTimeout(async () => {
          try {
            console.log("Triggering statistics collection after device toggle");
            const statsResponse = await fetch(`/api/statistics/collect`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                userId: userId || '',
                householdId: householdId || ''
              }),
            });
            
            if (statsResponse.ok) {
              console.log("Statistics collection triggered successfully after toggle");
            } else {
              console.warn("Failed to trigger statistics collection after toggle");
            }
          } catch (statsError) {
            console.error("Error triggering statistics collection:", statsError);
          }
        }, 1000); // Add a 1-second delay to ensure backend processing
      } catch (error) {
        console.error("Error updating device in backend:", error);
        // Continue with local update even if backend fails
        toast({
          title: "Warning",
          description: "Device updated locally but sync with server failed.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Error toggling device:", error);
      toast({
        title: "Error",
        description: "Failed to toggle device. Please try again.",
        variant: "destructive",
      });
      // If there was a critical error, revert the local change
      const originalDevices = JSON.parse(localStorage.getItem("devices") || "[]");
      setDevices(originalDevices);
    }
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (active.id !== over?.id) {
      setWidgets((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id)
        const newIndex = items.findIndex((item) => item.id === over?.id)

        const newOrder = arrayMove(items, oldIndex, newIndex)

        // Save the new order to localStorage
        localStorage.setItem("dashboardWidgets", JSON.stringify(newOrder))

        return newOrder
      })
    }
  }

  const toggleEditMode = () => {
    setIsEditing(!isEditing)
  }

  const saveLayout = () => {
    localStorage.setItem("dashboardWidgets", JSON.stringify(widgets))
    setIsEditing(false)
  }

  const cancelEditing = () => {
    // Reload the saved layout
    const storedWidgets = localStorage.getItem("dashboardWidgets")
    if (storedWidgets) {
      setWidgets(JSON.parse(storedWidgets))
    } else {
      initializeWidgets()
    }
    setIsEditing(false)
  }

  const activeDevices = devices.filter((d) => d.status === "on").length
  const totalDevices = devices.length

  // Render the Energy and Weather Section
  const renderEnergyWeatherSection = () => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="md:col-span-2 min-h-[400px]">
        <EnergyUsageWidget data={sampleEnergyData} />
      </div>
      <WeatherEnergyWidget city="Dubai" units="metric" />
    </div>
  )

  // Render the Room Consumption Widget
  const renderRoomConsumptionSection = () => (
    <RoomConsumptionWidget rooms={rooms} devices={devices} calculateRoomEnergy={calculateRoomEnergy} />
  )

  // Render the Rooms Section
  const renderRoomsSection = () => (
    <div className="pt-8">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Your Rooms</h2>
        <Link href="/add-room">
          <Button variant="outline" size="sm">
            <Plus className="mr-2 h-4 w-4" /> Add Room
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {rooms.map((room) => (
          <Card key={room.id} className="overflow-hidden">
            <div className="relative h-40">
              <Image
                src={
                  room.image ||
                  "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/IMG_0697-MRkZkq9qJMNVm20BYSDpYOdkYHt3pF.jpeg" ||
                  "/placeholder.svg" ||
                  "/placeholder.svg" ||
                  "/placeholder.svg" ||
                  "/placeholder.svg" ||
                  "/placeholder.svg" ||
                  "/placeholder.svg" ||
                  "/placeholder.svg" ||
                  "/placeholder.svg" ||
                  "/placeholder.svg" ||
                  "/placeholder.svg"
                }
                alt={room.name}
                fill
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
              <div className="absolute bottom-4 left-4 text-white">
                <h3 className="font-semibold text-lg capitalize">{room.name}</h3>
                <p className="text-sm text-white/80">{devices.filter((d) => d.room === room.name).length} devices</p>
              </div>
            </div>
            <CardContent className="p-4">
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Energy Usage</span>
                  <span className="text-sm font-bold text-[#00B2FF]">
                    {calculateRoomEnergy(room.name).toFixed(1)} kWh
                  </span>
                </div>
                <div className="space-y-2">
                  {devices
                    .filter((device) => device.room === room.name)
                    .slice(0, 3)
                    .map((device) => (
                      <div key={device.id} className="flex justify-between items-center">
                        <div className="flex items-center">
                          <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center ${device.status === "on" ? "bg-green-100" : "bg-gray-100"}`}
                          >
                            {getDeviceIcon(device.type)}
                          </div>
                          <span className="ml-2 text-sm">{device.name}</span>
                        </div>
                        <Switch
                          checked={device.status === "on"}
                          onCheckedChange={(checked) => toggleDevice(device.id, checked)}
                          className="data-[state=checked]:bg-[#00B2FF]"
                        />
                      </div>
                    ))}
                  {devices.filter((device) => device.room === room.name).length > 3 && (
                    <Link href={`/rooms/${room.id}`}>
                      <Button variant="ghost" size="sm" className="w-full text-[#00B2FF]">
                        View all devices
                      </Button>
                    </Link>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )

  // Render the Automations Section
  const renderAutomationsSection = () => (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Active Automations</h2>
        <Link href="/automations">
          <Button variant="outline" size="sm">
            <Plus className="mr-2 h-4 w-4" /> Add Automation
          </Button>
        </Link>
      </div>

      {automations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {automations
            .filter((automation) => automation.active)
            .slice(0, 3)
            .map((automation) => (
              <Card key={automation.id} className="overflow-hidden">
                <CardHeader className="bg-gradient-to-r from-[#00B2FF] to-[#0085FF] text-white p-4">
                  <CardTitle className="text-lg font-medium flex items-center justify-between">
                    <span>{automation.name}</span>
                    {getAutomationIcon(automation.icon)}
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-4">
                  <p className="text-sm text-gray-600 mb-2">{automation.description}</p>
                  <div className="flex items-center text-xs text-gray-500">
                    <Clock className="h-3 w-3 mr-1" />
                    <span>
                      {automation.schedule.startTime} - {automation.schedule.endTime}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
        </div>
      ) : (
        <Card className="bg-white p-6">
          <div className="flex flex-col items-center text-center space-y-4">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
              <Clock className="h-6 w-6 text-[#00B2FF]" />
            </div>
            <div>
              <h3 className="font-semibold">No Automations Yet</h3>
              <p className="text-sm text-gray-500 mb-4">Create automations to make your home smarter</p>
              <Link href="/automations">
                <Button className="bg-[#00B2FF] hover:bg-[#00B2FF]/90">
                  <Plus className="mr-2 h-4 w-4" /> Create Automation
                </Button>
              </Link>
            </div>
          </div>
        </Card>
      )}

      {automations.length > 3 && (
        <div className="flex justify-center mt-4">
          <Link href="/automations">
            <Button variant="outline">View all automations</Button>
          </Link>
        </div>
      )}
    </div>
  )

  // Render the Energy Saving Tips Section
  const renderSuggestionsSection = () => (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Energy Saving Tips</h2>
        <Link href="/suggestions">
          <Button variant="outline" size="sm">
            View All <ChevronRight className="ml-1 h-4 w-4" />
          </Button>
        </Link>
      </div>

      {suggestions.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {suggestions.map((suggestion, index) => (
            <Card key={index} className="overflow-hidden">
              <CardContent className="p-4">
                <div className="flex items-start space-x-4">
                  <div className="bg-blue-50 p-2 rounded-full">
                    <suggestion.icon className={`h-5 w-5 ${suggestion.iconColor}`} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-sm mb-1">{suggestion.title}</h3>
                    <p className="text-xs text-gray-500 mb-2">{suggestion.description}</p>
                    <Badge variant="outline" className="text-[#00B2FF] text-xs">
                      {suggestion.saving}
                    </Badge>
                    {suggestion.action && (
                      <div className="mt-2">
                        <Button variant="ghost" size="sm" className="h-7 px-2 text-xs">
                          {suggestion.action}
                        </Button>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-white p-6">
          <div className="flex flex-col items-center text-center space-y-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <Leaf className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold">No Energy Saving Tips Yet</h3>
              <p className="text-sm text-gray-500 mb-4">
                Add more devices and use them for a while to get personalized energy-saving suggestions
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  )

  // Render the Devices Section
  const renderDevicesSection = () => (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Your Devices</h2>
        <Link href="/add-device">
          <Button variant="outline" size="sm">
            <Plus className="mr-2 h-4 w-4" /> Add Device
          </Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {devices.slice(0, 6).map((device) => (
          <Card key={device.id} className="overflow-hidden">
            <CardContent className="p-4">
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center ${device.status === "on" ? "bg-green-100" : "bg-gray-100"}`}
                  >
                    {getDeviceIcon(device.type)}
                  </div>
                  <div className="ml-3">
                    <h3 className="font-semibold">{device.name}</h3>
                    <p className="text-xs text-gray-500">{device.room}</p>
                  </div>
                </div>
                <Switch
                  checked={device.status === "on"}
                  onCheckedChange={(checked) => toggleDevice(device.id, checked)}
                  className="data-[state=checked]:bg-[#00B2FF]"
                />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {devices.length > 6 && (
        <div className="flex justify-center mt-4">
          <Link href="/devices">
            <Button variant="outline">View all devices</Button>
          </Link>
        </div>
      )}
    </div>
  )

  // Render widget based on type
  const renderWidget = (widget: Widget) => {
    switch (widget.type) {
      case "energy-weather":
        return renderEnergyWeatherSection()
      case "room-consumption":
        return renderRoomConsumptionSection()
      case "rooms":
        return renderRoomsSection()
      case "automations":
        return renderAutomationsSection()
      case "suggestions":
        return renderSuggestionsSection()
      case "devices":
        return renderDevicesSection()
      default:
        return null
    }
  }

  // Log current state
  console.log("Dashboard render state:", {
    roomsCount: rooms.length,
    devicesCount: devices.length,
    loading
  });

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <NavigationSidebar />
        <div className="flex-1 ml-[72px] p-6 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#00B2FF] mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading your smart home dashboard...</p>
          </div>
        </div>
      </div>
    );
  }

  // Check if we need to show the empty state (no rooms AND no devices)
  if (rooms.length === 0 && devices.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <NavigationSidebar />
        <div className="flex-1 ml-[72px]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Header */}
          <header className="flex justify-between items-center mb-8">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">Sy</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
                <p className="text-sm text-gray-500">Your smart home overview</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <VoiceAssistant devices={devices} rooms={rooms} toggleDevice={toggleDevice} />
              <Button variant="outline" className="text-[#00B2FF]" onClick={() => setGuideOpen(true)}>
                <FileText className="h-4 w-4 mr-2" /> View Guide
              </Button>
            </div>
          </header>

          {/* Welcome Card */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <Card className="mb-8">
              <CardContent className="flex flex-col items-center text-center py-16">
                <div className="w-20 h-20 bg-[#00B2FF]/10 rounded-full flex items-center justify-center mb-6">
                  <Home className="w-10 h-10 text-[#00B2FF]" />
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-3">Welcome to your Smart Home</h2>
                <p className="text-gray-500 mb-8 max-w-md">
                  It looks like you haven't added any rooms or devices yet. Let's get started by setting up your home.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md">
                  <Link href="/add-room" className="flex-1">
                    <Button className="w-full bg-[#00B2FF] hover:bg-[#00B2FF]/90 h-12">
                      <Home className="mr-2 h-5 w-5" />
                      Add Your First Room
                    </Button>
                  </Link>
                  <Button
                    variant="outline"
                    className="w-full border-gray-300 text-gray-700 hover:bg-gray-100 h-12"
                    onClick={() => setGuideOpen(true)}
                  >
                    <Info className="mr-2 h-5 w-5" />
                    How It Works
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* PDF Viewer Dialog */}
        <Dialog open={guideOpen} onOpenChange={setGuideOpen}>
          <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
            <DialogHeader>
              <DialogTitle>Smart Home Energy Guide</DialogTitle>
            </DialogHeader>
            <Tabs defaultValue="overview" className="flex-1 flex flex-col">
              <TabsList className="mx-auto mb-4">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="setup">Setup Guide</TabsTrigger>
                <TabsTrigger value="energy">Energy Saving</TabsTrigger>
                <TabsTrigger value="faq">FAQ</TabsTrigger>
              </TabsList>
              <div className="flex-1 overflow-auto border rounded-md p-4 bg-white">
                  {/* Tab content stays the same */}
              </div>
            </Tabs>
          </DialogContent>
        </Dialog>
        </div>
      </div>
    )
  }

  // Check if we need to show the "add device" state (has rooms but no devices)
  if (rooms.length > 0 && devices.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <NavigationSidebar />
        <div className="flex-1 ml-[72px]">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            {/* Header */}
            <header className="flex justify-between items-center mb-8">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-xl">Sy</span>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
                  <p className="text-sm text-gray-500">Your smart home overview</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <VoiceAssistant devices={devices} rooms={rooms} toggleDevice={toggleDevice} />
                <Button variant="outline" className="text-[#00B2FF]" onClick={() => setGuideOpen(true)}>
                  <FileText className="h-4 w-4 mr-2" /> View Guide
                </Button>
              </div>
            </header>

            {/* Welcome Card */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
              <Card className="mb-8">
                <CardContent className="flex flex-col items-center text-center py-16">
                  <div className="w-20 h-20 bg-[#FF9500]/10 rounded-full flex items-center justify-center mb-6">
                    <Smartphone className="w-10 h-10 text-[#FF9500]" />
                  </div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-3">Great! Now Add Your First Device</h2>
                  <p className="text-gray-500 mb-8 max-w-md">
                    You've added {rooms.length} {rooms.length === 1 ? "room" : "rooms"}. Now let's add some devices to
                    monitor and control.
                  </p>
                  <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md">
                    <Link href="/add-device" className="flex-1">
                      <Button className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 h-12">
                        <Smartphone className="mr-2 h-5 w-5" />
                        Add Your First Device
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
            
            {/* Weather Widget */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="mb-8"
            >
              <WeatherEnergyWidget city="Dubai" units="metric" />
            </motion.div>

            {/* Rooms Section */}
            <div className="mb-8">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Your Rooms</h2>
                <Link href="/add-room">
                  <Button variant="outline" size="sm">
                    <Plus className="mr-2 h-4 w-4" /> Add Room
                  </Button>
                </Link>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {rooms.map((room) => (
                  <Card key={room.id} className="overflow-hidden">
                    <div className="relative h-40">
                      <Image
                        src={
                          room.image ||
                          "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/IMG_0697-MRkZkq9qJMNVm20BYSDpYOdkYHt3pF.jpeg" ||
                          "/placeholder.svg"
                        }
                        alt={room.name}
                        fill
                        className="object-cover"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                      <div className="absolute bottom-4 left-4 text-white">
                        <h3 className="font-semibold text-lg capitalize">{room.name}</h3>
                        <p className="text-sm text-white/80">No devices yet</p>
                      </div>
                    </div>
                    <CardContent className="p-4">
                      <div className="flex justify-center">
                        <Link href="/add-device">
                          <Button variant="outline" size="sm" className="text-[#00B2FF]">
                            <Plus className="mr-2 h-4 w-4" /> Add Device to {room.name}
                          </Button>
                        </Link>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8"
            >
              <Card>
                <CardContent className="p-6">
                  <div className="flex flex-col items-center text-center space-y-4">
                    <div className="w-12 h-12 bg-[#FF9500]/10 rounded-full flex items-center justify-center">
                      <Smartphone className="w-6 h-6 text-[#FF9500]" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Add Devices</h3>
                      <p className="text-sm text-gray-500 mb-4">Connect your smart devices to monitor energy usage</p>
                      <Link href="/add-device">
                        <Button variant="outline" size="sm">
                          <Plus className="mr-2 h-4 w-4" /> Add Device
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex flex-col items-center text-center space-y-4">
                    <div className="w-12 h-12 bg-[#00B2FF]/10 rounded-full flex items-center justify-center">
                      <Home className="w-6 h-6 text-[#00B2FF]" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Add More Rooms</h3>
                      <p className="text-sm text-gray-500 mb-4">Create more rooms to organize your smart devices</p>
                      <Link href="/add-room">
                        <Button variant="outline" size="sm">
                          <Plus className="mr-2 h-4 w-4" /> Add Room
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-6">
                  <div className="flex flex-col items-center text-center space-y-4">
                    <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                      <Zap className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Energy Tips</h3>
                      <p className="text-sm text-gray-500 mb-4">Discover ways to reduce your energy consumption</p>
                      <Link href="/suggestions">
                        <Button variant="outline" size="sm">
                          View Tips
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* PDF Viewer Dialog */}
          <Dialog open={guideOpen} onOpenChange={setGuideOpen}>
            <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
              <DialogHeader>
                <DialogTitle>Smart Home Energy Guide</DialogTitle>
              </DialogHeader>
              <Tabs defaultValue="overview" className="flex-1 flex flex-col">
                <TabsList className="mx-auto mb-4">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="setup">Setup Guide</TabsTrigger>
                  <TabsTrigger value="energy">Energy Saving</TabsTrigger>
                  <TabsTrigger value="faq">FAQ</TabsTrigger>
                </TabsList>
                <div className="flex-1 overflow-auto border rounded-md p-4 bg-white">
                  {/* Tab content stays the same */}
                </div>
              </Tabs>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    )
  }

  // If we have devices but no rooms, we should still show the main dashboard
  if (devices.length > 0 && rooms.length === 0) {
    // Main dashboard view for the case where we have devices but no rooms
    return (
      <motion.div initial="hidden" animate="visible" className="min-h-screen bg-gray-50 flex">
        <NavigationSidebar />
        <div className="flex-1 ml-[72px] p-6">
          <header className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">Sy</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
                <p className="text-sm text-gray-500">Your smart home overview</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <VoiceAssistant devices={devices} rooms={rooms} toggleDevice={toggleDevice} />
              <Button variant="outline" className="text-[#00B2FF]" onClick={() => setGuideOpen(true)}>
                <FileText className="h-4 w-4 mr-2" /> View Guide
              </Button>
            </div>
          </header>

          <div className="space-y-12">
            {/* Energy Weather Section */}
            {renderEnergyWeatherSection()}
            
            {/* Devices Section */}
            {renderDevicesSection()}
            
            {/* Add Room Prompt */}
            <Card className="bg-blue-50 border-blue-100">
              <CardContent className="p-6">
                <div className="flex flex-col items-center text-center space-y-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <Home className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-blue-900">Add Rooms to Organize Your Devices</h3>
                    <p className="text-sm text-blue-700 mb-4">Create rooms to better organize and manage your smart devices</p>
                    <Link href="/add-room">
                      <Button className="bg-[#00B2FF] hover:bg-[#00B2FF]/90">
                        <Plus className="mr-2 h-4 w-4" /> Add Your First Room
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {/* Suggestions Section */}
            {renderSuggestionsSection()}
          </div>

          {/* PDF Viewer Dialog */}
          <Dialog open={guideOpen} onOpenChange={setGuideOpen}>
            <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
              <DialogHeader>
                <DialogTitle>Smart Home Energy Guide</DialogTitle>
              </DialogHeader>
              <Tabs defaultValue="overview" className="flex-1 flex flex-col">
                <TabsList className="mx-auto mb-4">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="setup">Setup Guide</TabsTrigger>
                  <TabsTrigger value="energy">Energy Saving</TabsTrigger>
                  <TabsTrigger value="faq">FAQ</TabsTrigger>
                </TabsList>
                <div className="flex-1 overflow-auto border rounded-md p-4 bg-white">
                  {/* Tab content stays the same */}
                </div>
              </Tabs>
            </DialogContent>
          </Dialog>
        </div>
      </motion.div>
    )
  }

  // Main dashboard view with both rooms and devices
  return (
    <motion.div initial="hidden" animate="visible" className="min-h-screen bg-gray-50 flex">
      <NavigationSidebar />
      <div className="flex-1 ml-[72px] p-6">
        <header className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">Sy</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
              <p className="text-sm text-gray-500">Your smart home overview</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <VoiceAssistant devices={devices} rooms={rooms} toggleDevice={toggleDevice} />
            {isEditing ? (
              <>
                <Button variant="outline" size="sm" onClick={cancelEditing} className="flex items-center gap-1">
                  <X className="h-4 w-4" /> Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={saveLayout}
                  className="bg-[#00B2FF] hover:bg-[#00B2FF]/90 flex items-center gap-1"
                >
                  <Check className="h-4 w-4" /> Save Layout
                </Button>
              </>
            ) : (
              <Button variant="outline" size="sm" onClick={toggleEditMode} className="flex items-center gap-1">
                <Move className="h-4 w-4 mr-1" /> Customize Layout
              </Button>
            )}
            <Button variant="outline" className="text-[#00B2FF]" onClick={() => setGuideOpen(true)}>
              <FileText className="h-4 w-4 mr-2" /> View Guide
            </Button>
          </div>
        </header>

        <div className="space-y-12">
          {/* Draggable Widgets */}
          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
            modifiers={[restrictToParentElement]}
          >
            <SortableContext items={widgets.map((w) => w.id)} strategy={rectSortingStrategy}>
              <div className="space-y-12">
                {widgets.map((widget) => (
                  <SortableWidget key={widget.id} id={widget.id} isEditing={isEditing}>
                    {renderWidget(widget)}
                  </SortableWidget>
                ))}
              </div>
            </SortableContext>
          </DndContext>
        </div>

        {/* PDF Viewer Dialog */}
        <Dialog open={guideOpen} onOpenChange={setGuideOpen}>
          <DialogContent className="max-w-4xl h-[80vh] flex flex-col">
            <DialogHeader>
              <DialogTitle>Smart Home Energy Guide</DialogTitle>
            </DialogHeader>
            <Tabs defaultValue="overview" className="flex-1 flex flex-col">
              <TabsList className="mx-auto mb-4">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="setup">Setup Guide</TabsTrigger>
                <TabsTrigger value="energy">Energy Saving</TabsTrigger>
                <TabsTrigger value="faq">FAQ</TabsTrigger>
              </TabsList>
              <div className="flex-1 overflow-auto border rounded-md p-4 bg-white">
                  {/* Tab content stays the same */}
              </div>
            </Tabs>
          </DialogContent>
        </Dialog>
      </div>
    </motion.div>
  )
}

