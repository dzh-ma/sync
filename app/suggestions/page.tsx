"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Download,
  User,
  Lightbulb,
  ThermometerSun,
  Timer,
  Fan,
  ArrowRight,
  Zap,
  AlertTriangle,
  Info,
  PlusCircle,
  Bell,
  CircleCheck,
} from "lucide-react"
import { motion } from "framer-motion"
import Link from "next/link"
import { useToast } from "@/components/ui/use-toast"
import { useRouter } from "next/navigation"
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog"
import { NavigationSidebar } from "@/app/components/navigation-sidebar"
import axios from "axios"

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Function to calculate power consumption based on device type and settings
const calculateDevicePower = (device: any): number => {
  if (!device) return 0;
  
  // Use the device's specific basePowerConsumption value or default
  const basePower = device.basePowerConsumption || 10;
  
  // Apply modifiers based on device type and settings
  switch (device.type) {
    case "light":
      // Brightness affects power (0-100%)
      return basePower * (device.brightness || 100) / 100;
    
    case "thermostat":
      // Higher temperature difference from ambient (assumed 22°C) increases power
      const tempDiff = Math.abs((device.temperature || 22) - 22);
      return basePower * (1 + tempDiff / 10);
    
    case "fan":
      // Fan speed affects power (1-5)
      const speedMultiplier: Record<number, number> = {
        1: 0.6,  // Low speed
        2: 0.8,  // Medium speed
        3: 1.0,  // High speed
        4: 1.2,  // Higher speed
        5: 1.5   // Highest speed
      };
      const currentSpeed = device.speed || 2;
      return basePower * (speedMultiplier[currentSpeed] || 0.8);
    
    default:
      return basePower;
  }
};

// Icon mapping for dynamic icon rendering
const iconMap: { [key: string]: any } = {
  Lightbulb,
  ThermometerSun,
  Timer,
  Fan,
  Zap,
  Clock: Timer,
  Thermometer: ThermometerSun,
  Tv: () => (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <rect x="2" y="7" width="20" height="15" rx="2" ry="2"></rect>
      <polyline points="17 2 12 7 7 2"></polyline>
    </svg>
  ),
}

// Define Device interface
interface Device {
  id: string
  name: string
  type: string
  room: string
  status: "on" | "off"
  brightness?: number
  temperature?: number
  speed?: number
  powerConsumption?: number
  basePowerConsumption?: number
  totalEnergyConsumed?: number
  lastStatusChange?: number
}

interface Suggestion {
  title: string
  description: string
  icon: string
  iconColor: string
  saving: string
  impact?: string
  action?: string
  details?: string[]
  category?: string
  deviceId?: string
}

export default function SuggestionsPage() {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [noDevices, setNoDevices] = useState(false)
  const [noActiveSuggestions, setNoActiveSuggestions] = useState(false)
  const [userType, setUserType] = useState<"admin" | "household">("admin")
  const [hasNewSuggestions, setHasNewSuggestions] = useState(false)
  const { toast } = useToast()
  const router = useRouter()

  // Update the handleActionClick function and add dialog state variables
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [optimizationSuccess, setOptimizationSuccess] = useState(false)
  const [currentSuggestion, setCurrentSuggestion] = useState<Suggestion | null>(null)
  const [optimizationProgress, setOptimizationProgress] = useState(0)

  const handleActionClick = (suggestion: Suggestion) => {
    if (suggestion.action === "Adjust Settings") {
      // Open the optimization dialog
      setCurrentSuggestion(suggestion)
      setIsOptimizing(true)
      setOptimizationSuccess(false)
      setOptimizationProgress(0)

      // Start the optimization process
      optimizeDevice(suggestion)
    } else if (suggestion.deviceId) {
      // Navigate to the device page with the device ID
      router.push(`/devices/${suggestion.deviceId}`)
    } else if (suggestion.action === "Create Automation") {
      // Remove this suggestion from the list
      setSuggestions((prevSuggestions) => {
        const updatedSuggestions = prevSuggestions.filter(
          (s) => !(s.title === suggestion.title && s.action === "Create Automation")
        )
        
        // If no suggestions left, show the no suggestions state
        if (updatedSuggestions.length === 0) {
          setNoActiveSuggestions(true)
        }
        
        // Save updated suggestions to localStorage
        localStorage.setItem("suggestions", JSON.stringify(updatedSuggestions))
        
        return updatedSuggestions
      })
      
      // Navigate to the automations page
      router.push("/automations")
    }
  }

  // Add the optimizeDevice function with more aggressive optimization
  const optimizeDevice = async (suggestion: Suggestion) => {
    if (!suggestion.deviceId) return

    // Simulate processing time with progress updates
    const progressInterval = setInterval(() => {
      setOptimizationProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return 90
        }
        return prev + 10
      })
    }, 200)

    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Get the devices from localStorage
    const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]")
    const deviceToOptimize = storedDevices.find((d: Device) => d.id === suggestion.deviceId)

    if (!deviceToOptimize) {
      setIsOptimizing(false)
      clearInterval(progressInterval)
      toast({
        title: "Device not found",
        description: "The device you're trying to optimize couldn't be found.",
        variant: "destructive",
      })
      return
    }

    // Determine what to optimize based on the suggestion title/description
    const updatedDevice = { ...deviceToOptimize }

    if (suggestion.title.includes("Brightness")) {
      // Reduce brightness by 50% but not below 50%
      const currentBrightness = deviceToOptimize.brightness || 100
      const newBrightness = Math.max(50, Math.floor(currentBrightness / 2))
      updatedDevice.brightness = newBrightness
    } else if (suggestion.title.includes("Fan Speed")) {
      // Reduce fan speed by about 50%
      const currentSpeed = deviceToOptimize.speed || 5
      const newSpeed = Math.max(1, Math.floor(currentSpeed / 2))
      updatedDevice.speed = newSpeed
    } else if (suggestion.title.includes("Temperature")) {
      // Adjust temperature more aggressively
      const currentTemp = deviceToOptimize.temperature || 24
      
      // Make very significant adjustments to ensure the change is noticeable
      // Set to optimal temperature based on energy efficiency guidelines
      if (currentTemp < 22) {
        // If in cooling mode, set to 25°C (more energy efficient)
        updatedDevice.temperature = 25
      } else if (currentTemp > 24) {
        // If in heating mode, set to 20°C (more energy efficient)
        updatedDevice.temperature = 20
      } else {
        // If already in optimal range, set to exact middle of range
        updatedDevice.temperature = 22.5
      }
      
      // Force status to "on" to ensure changes take effect
      updatedDevice.status = "on"
      
      console.log(`Optimizing thermostat from ${currentTemp}°C to ${updatedDevice.temperature}°C`)
    } else if (suggestion.title.includes("Usage")) {
      // If it's a usage suggestion, just mark it as optimized
      // No specific setting to adjust
    }

    try {
      // Get user info from localStorage
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
      
      if (!userId) {
        console.error("No user ID found")
        toast({
          title: "Error",
          description: "User information not found. Please login again.",
          variant: "destructive",
        })
        return
      }

      // Calculate new power consumption based on updated settings
      const calculatedPower = calculateDevicePower(updatedDevice)
      
      // Update in backend based on what was changed
      if (updatedDevice.brightness !== undefined && updatedDevice.brightness !== deviceToOptimize.brightness) {
        await axios.post(`${API_URL}/api/user/update-device-settings`, {
          user_id: userId,
          household_id: householdId,
          device_name: deviceToOptimize.name,
          settings: {
            brightness: updatedDevice.brightness
          },
          calculated_power: calculatedPower
        })
      } else if (updatedDevice.speed !== undefined && updatedDevice.speed !== deviceToOptimize.speed) {
        await axios.post(`${API_URL}/api/user/update-device-settings`, {
          user_id: userId,
          household_id: householdId,
          device_name: deviceToOptimize.name,
          settings: {
            speed: updatedDevice.speed
          },
          calculated_power: calculatedPower
        })
      } else if (updatedDevice.temperature !== undefined && updatedDevice.temperature !== deviceToOptimize.temperature) {
        console.log(`Sending temperature update to backend: ${updatedDevice.temperature}°C (was ${deviceToOptimize.temperature}°C)`)
        try {
          const response = await axios.post(`${API_URL}/api/user/update-device-settings`, {
            user_id: userId,
            household_id: householdId,
            device_name: deviceToOptimize.name,
            settings: {
              temperature: updatedDevice.temperature
            },
            calculated_power: calculatedPower
          });
          console.log("Temperature update response:", response.data);
          
          // Also update the device status if we changed it
          if (updatedDevice.status !== deviceToOptimize.status) {
            console.log(`Also updating device status to: ${updatedDevice.status}`);
            await axios.put(`${API_URL}/api/user/toggle-device`, null, {
              params: {
                user_id: userId,
                device_name: deviceToOptimize.name,
                household_id: householdId,
                status: updatedDevice.status,
              }
            });
          }
        } catch (error) {
          console.error("Error updating temperature:", error);
          // Continue with local updates even if backend fails
        }
      }

      // Update the device in localStorage
      const updatedDevices = storedDevices.map((d: Device) => (d.id === suggestion.deviceId ? updatedDevice : d))
      localStorage.setItem("devices", JSON.stringify(updatedDevices))

      // Update UI
      setOptimizationProgress(100)
      await new Promise((resolve) => setTimeout(resolve, 500))
      setOptimizationSuccess(true)
      clearInterval(progressInterval)

      // Close dialog after showing success
      setTimeout(() => {
        setIsOptimizing(false)

        // Show success toast
        toast({
          title: "Device Optimized",
          description: `Successfully optimized ${deviceToOptimize.name} for energy savings.`,
        })

        // Update suggestions list by removing the applied suggestion
        setSuggestions((prevSuggestions) => {
          const updatedSuggestions = prevSuggestions.filter(
            (s) => !(s.title === suggestion.title && s.deviceId === suggestion.deviceId),
          )

          // If no suggestions left, show the no suggestions state
          if (updatedSuggestions.length === 0) {
            setNoActiveSuggestions(true)
          }

          // Save updated suggestions to localStorage
          localStorage.setItem("suggestions", JSON.stringify(updatedSuggestions))

          return updatedSuggestions
        })
      }, 1500)
    } catch (error) {
      console.error("Error optimizing device:", error)
      clearInterval(progressInterval)
      setIsOptimizing(false)
      toast({
        title: "Optimization Failed",
        description: "There was an error optimizing your device. Please try again.",
        variant: "destructive",
      })
    }
  }

  useEffect(() => {
    let isMounted = true

    const fetchSuggestions = async () => {
      try {
        // Get devices from localStorage
        const storedDevices = localStorage.getItem("devices")
        const devices = storedDevices ? JSON.parse(storedDevices) : []

        // If no devices, set appropriate state and return early
        if (!devices || devices.length === 0) {
          if (isMounted) {
            setNoDevices(true)
            setLoading(false)
          }
          return
        }

        // Get current user type
        const currentUser = JSON.parse(localStorage.getItem("currentUser") || '{"type": "admin"}')
        if (isMounted) {
          setUserType(currentUser.type)
        }

        // Get previously stored suggestions
        const storedSuggestions = localStorage.getItem("suggestions")
        const previousSuggestions = storedSuggestions ? JSON.parse(storedSuggestions) : []

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
          throw new Error(`Failed to fetch suggestions: ${response.status}`)
        }

        const data = await response.json()

        if (isMounted) {
          setSuggestions(data.suggestions || [])
          setNoDevices(data.noDevices || false)
          setNoActiveSuggestions(data.hasDevices && !data.hasActiveSuggestions)
          setHasNewSuggestions(data.hasNewSuggestions || false)

          // Store the current suggestions
          localStorage.setItem("suggestions", JSON.stringify(data.suggestions || []))

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
        }
      } catch (err: any) {
        console.error("Error fetching suggestions:", err)
        if (isMounted) {
          setError(err.message || "Failed to fetch suggestions")
          // Set fallback state
          setNoActiveSuggestions(true)
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    // Initial fetch
    fetchSuggestions()

    // Set up polling interval
    const interval = setInterval(fetchSuggestions, 5 * 60 * 1000)

    // Cleanup function
    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [toast])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
    },
  }

  // Render loading state
  if (loading) {
    return (
      <div className="flex">
        <NavigationSidebar />
        <div className="p-6 bg-gray-50 min-h-screen flex-1 ml-[72px] flex items-center justify-center">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-t-[#00B2FF] border-[#FF9500]/20 rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading suggestions...</p>
          </div>
        </div>
      </div>
    )
  }

  // Render error state
  if (error) {
    return (
      <div className="flex">
        <NavigationSidebar />
        <div className="p-6 bg-gray-50 min-h-screen flex-1 ml-[72px]">
          <Card className="border-red-200">
            <CardContent className="pt-6">
              <div className="flex flex-col items-center text-center gap-4">
                <AlertTriangle className="h-12 w-12 text-red-500" />
                <h2 className="text-xl font-semibold text-gray-800">Something went wrong</h2>
                <p className="text-gray-600">{error}</p>
                <Button onClick={() => window.location.reload()}>Try Again</Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Render no devices state
  if (noDevices) {
    return (
      <div className="flex">
        <NavigationSidebar />
        <motion.div
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="p-6 bg-gray-50 min-h-screen flex-1 ml-[72px]"
        >
          <motion.header variants={itemVariants} className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Smart Suggestions</h1>
                <p className="text-sm text-gray-500">Optimize your home's energy usage</p>
              </div>
            </div>
          </motion.header>

          <motion.div variants={itemVariants}>
            <Card className="overflow-hidden border-blue-100">
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center gap-6 py-10">
                  <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center">
                    <PlusCircle className="h-10 w-10 text-blue-500" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-800 mb-2">No devices found</h2>
                    <p className="text-gray-600 max-w-md mx-auto mb-4">
                      Add devices to your smart home to receive personalized energy-saving suggestions and tips.
                    </p>
                    <div className="bg-blue-50 p-4 rounded-lg mb-6 max-w-md mx-auto">
                      <h3 className="font-medium text-blue-700 flex items-center gap-2 mb-2">
                        <Info className="h-4 w-4" /> Energy Saving Tip
                      </h3>
                      <p className="text-sm text-blue-600">
                        Smart devices can help reduce your energy consumption by up to 15% through automated scheduling
                        and optimized usage patterns.
                      </p>
                    </div>
                    <Link href="/add-device">
                      <Button className="bg-[#00B2FF] hover:bg-[#0085FF]">
                        Add Your First Device
                        <ArrowRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </div>
    )
  }

  // Render no active suggestions state
  if (noActiveSuggestions) {
    return (
      <div className="flex">
        <NavigationSidebar />
        <motion.div
          initial="hidden"
          animate="visible"
          variants={containerVariants}
          className="p-6 bg-gray-50 min-h-screen flex-1 ml-[72px]"
        >
          <motion.header variants={itemVariants} className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                <Lightbulb className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Smart Suggestions</h1>
                <p className="text-sm text-gray-500">Optimize your home's energy usage</p>
              </div>
            </div>
          </motion.header>

          <motion.div variants={itemVariants}>
            <Card className="overflow-hidden border-green-100">
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center gap-6 py-10">
                  <div className="w-20 h-20 bg-green-50 rounded-full flex items-center justify-center">
                    <CircleCheck className="h-10 w-10 text-green-500" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-gray-800 mb-2">All Optimized!</h2>
                    <p className="text-gray-600 max-w-md mx-auto mb-4">
                      Your devices are running efficiently! We'll notify you when we detect new opportunities to save
                      energy.
                    </p>
                    <div className="bg-green-50 p-4 rounded-lg mb-6 max-w-md mx-auto">
                      <h3 className="font-medium text-green-700 flex items-center gap-2 mb-2">
                        <Info className="h-4 w-4" /> Energy Saving Tip
                      </h3>
                      <p className="text-sm text-green-600">
                        Regular maintenance of your devices can improve their efficiency and extend their lifespan,
                        saving both energy and money in the long run.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </div>
    )
  }

  // Render suggestions
  return (
    <div className="flex">
      <NavigationSidebar />
      <motion.div
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="p-6 bg-gray-50 min-h-screen flex-1 ml-[72px]"
      >
        <motion.header variants={itemVariants} className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Smart Suggestions</h1>
              <p className="text-sm text-gray-500">Optimize your home's energy usage</p>
            </div>
            {hasNewSuggestions && (
              <Badge variant="destructive" className="animate-pulse cursor-pointer">
                <Bell className="h-3 w-3 mr-1" /> New
              </Badge>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              className="text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF] hover:text-white"
            >
              <Download className="h-5 w-5" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF] hover:text-white"
            >
              <User className="h-5 w-5" />
            </Button>
          </div>
        </motion.header>

        <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {suggestions.map((suggestion, index) => {
            // Get the icon component from the map
            const IconComponent = (iconMap as any)[suggestion.icon] || Zap

            return (
              <motion.div key={`${suggestion.title}-${index}`} variants={itemVariants}>
                <Card className="overflow-hidden hover:shadow-lg transition-shadow duration-300">
                  <CardHeader className="bg-gradient-to-r from-[#00B2FF] to-[#0085FF] pb-8 relative">
                    <CardTitle className="text-white text-xl mb-2">{suggestion.title}</CardTitle>
                    <p className="text-white/80 text-sm">{suggestion.description}</p>
                    <div className="absolute bottom-0 right-0 transform translate-y-1/2 mr-6">
                      <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-lg">
                        <IconComponent className={`w-6 h-6 ${suggestion.iconColor}`} />
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-8">
                    <div className="space-y-4">
                      <div>
                        {suggestion.category && (
                          <Badge variant="secondary" className="mb-2">
                            {suggestion.category}
                          </Badge>
                        )}
                        <p className="text-sm font-medium text-green-600">{suggestion.saving}</p>
                        {suggestion.impact && <p className="text-sm text-gray-600">{suggestion.impact}</p>}
                      </div>
                      {suggestion.details && (
                        <div className="space-y-2">
                          {suggestion.details.map((detail, idx) => (
                            <div key={idx} className="flex items-center text-sm text-gray-600">
                              <div className="w-1.5 h-1.5 rounded-full bg-[#00B2FF] mr-2" />
                              {detail}
                            </div>
                          ))}
                        </div>
                      )}
                      {suggestion.action && (
                        <Button
                          className="w-full bg-[#00B2FF] hover:bg-[#00B2FF]/90"
                          onClick={() => handleActionClick(suggestion)}
                        >
                          {suggestion.action}
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )
          })}
        </motion.div>
      </motion.div>

      {/* Keep the Dialog component outside the flex container */}
      <Dialog open={isOptimizing} onOpenChange={(open) => !open && setIsOptimizing(false)}>
        <DialogContent className="sm:max-w-md">
          <DialogTitle className="sr-only">
            {!optimizationSuccess 
              ? `Optimizing ${currentSuggestion?.title.split(" ")[0]} Settings` 
              : "Optimization Complete"}
          </DialogTitle>
          <div className="flex flex-col items-center justify-center py-8">
            {!optimizationSuccess ? (
              <>
                <div className="w-16 h-16 mb-4 relative">
                  <div className="w-full h-full border-4 border-t-[#00B2FF] border-[#FF9500]/20 rounded-full animate-spin"></div>
                  <div className="absolute inset-0 flex items-center justify-center text-[#00B2FF]">
                    <Zap className="w-6 h-6" />
                  </div>
                </div>
                <h3 className="text-xl font-semibold mb-2">
                  Optimizing {currentSuggestion?.title.split(" ")[0]} Settings
                </h3>
                <p className="text-gray-500 text-center mb-2">Making energy-efficient adjustments to your device...</p>
                <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
                  <div
                    className="bg-gradient-to-r from-[#00B2FF] to-[#FF9500] h-2.5 rounded-full transition-all duration-300 ease-in-out"
                    style={{ width: `${optimizationProgress}%` }}
                  ></div>
                </div>
              </>
            ) : (
              <>
                <div className="w-16 h-16 bg-gradient-to-br from-[#00B2FF]/20 to-[#FF9500]/20 rounded-full flex items-center justify-center mb-4">
                  <CircleCheck className="w-8 h-8 text-[#00B2FF]" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Optimization Complete!</h3>
                <p className="text-gray-500 text-center">Your device has been optimized for energy efficiency.</p>
              </>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

