"use client"

import React from "react"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Clock, Sun, Moon, Home, Plus, Zap, Droplet, Thermometer, Trash2, Edit, Repeat } from "lucide-react"
import { motion } from "framer-motion"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { toast } from "@/components/ui/use-toast"
import { NavigationSidebar } from "@/app/components/navigation-sidebar"
import { usePermission } from "@/app/hooks/use-permissions"
import axios from "axios"
import { useRouter } from "next/navigation"
import { AutomationNotification } from "@/app/components/automation-notification"

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Automation {
  _id?: string
  id?: number
  name: string
  description: string
  icon: string
  active: boolean
  schedule: {
    type: "once" | "daily" | "weekly" | "custom"
    startTime: string
    endTime: string
    daysOfWeek?: number[]
  }
  devices: string[]
  user_id?: string
  household_id?: string
}

interface Device {
  id: string
  name: string
  type: string
  room: string
  status?: "on" | "off"
}

const automationIcons: Record<string, any> = {
  Sun,
  Moon,
  Home,
  Clock,
  Zap,
  Droplet,
  Thermometer,
}

const daysOfWeek = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

export default function AutomationsPage() {
  const { hasPermission } = usePermission("addAutomation")
  const router = useRouter()
  const [automations, setAutomations] = useState<Automation[]>([])
  const [devices, setDevices] = useState<Device[]>([])
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingAutomation, setEditingAutomation] = useState<Automation | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [user, setUser] = useState<any>(null)
  const [newAutomation, setNewAutomation] = useState<Automation>({
    name: "",
    description: "",
    icon: "Clock",
    active: true,
    schedule: {
      type: "once",
      startTime: "",
      endTime: "",
    },
    devices: [],
  })
  const [notifications, setNotifications] = useState<string[]>([])
  const [lastCheckTime, setLastCheckTime] = useState<Date>(new Date())
  const [expandedDeviceLists, setExpandedDeviceLists] = useState<Record<string, boolean>>({})

  useEffect(() => {
    // Load user data from localStorage
    const storedUser = localStorage.getItem("currentUser")
    const storedMember = localStorage.getItem("currentMember")
    
    if (storedUser) {
      setUser(JSON.parse(storedUser))
    } else if (storedMember) {
      setUser(JSON.parse(storedMember))
    } else {
      router.push("/auth/login")
      return
    }
  }, [router])

  useEffect(() => {
    if (user) {
      loadAutomations()
      loadDevices()
    }
  }, [user])

  const loadAutomations = async () => {
    try {
      setIsLoading(true)
      
      // Try to load from backend first
      try {
        const response = await axios.get(`${API_URL}/api/automations`, {
          params: {
            user_id: user.id || user.email,
            household_id: user.householdId
          }
        })
        
        if (response.data && Array.isArray(response.data)) {
          console.log("Loaded automations from backend:", response.data)
          setAutomations(response.data)
          return
        }
      } catch (error) {
        console.warn("Could not load automations from backend, falling back to localStorage")
      }
      
      // Fallback to localStorage if backend fails
      const storedAutomations = JSON.parse(localStorage.getItem("automations") || "[]")
      setAutomations(storedAutomations)
    } catch (error) {
      console.error("Error loading automations:", error)
      toast({
        title: "Error",
        description: "Failed to load automations. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const loadDevices = async () => {
    try {
      // Try to load from backend first
      try {
        const response = await axios.get(`${API_URL}/api/user/devices`, {
          params: {
            user_id: user.id || user.email,
            household_id: user.householdId
          }
        })
        
        if (response.data && Array.isArray(response.data)) {
          // Transform the devices to match our interface
          const transformedDevices = response.data.map((device: any) => ({
            id: device.device_name || device.name, // Using name as ID since that's what the backend uses
            name: device.device_name || device.name,
            type: device.deviceType || device.type,
            room: device.room,
            status: device.status
          }))
          
          console.log("Loaded devices from backend:", transformedDevices)
          setDevices(transformedDevices)
          return
        }
      } catch (error) {
        console.warn("Could not load devices from backend, falling back to localStorage")
      }
      
      // Fallback to localStorage if backend fails
      const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]")
      setDevices(storedDevices)
    } catch (error) {
      console.error("Error loading devices:", error)
      toast({
        title: "Error",
        description: "Failed to load devices. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleToggleAutomation = async (id: string | number, active: boolean) => {
    try {
      if (typeof id === 'string') {
        // Backend ID (MongoDB ObjectId as string)
        await axios.put(`${API_URL}/api/automations/toggle/${id}`, null, {
          params: { active }
        })
        
        // Update local state
        setAutomations(automations.map((automation) =>
          automation._id === id ? { ...automation, active } : automation
        ))
      } else {
        // Local ID (number from localStorage)
        const updatedAutomations = automations.map((automation) =>
          automation.id === id ? { ...automation, active } : automation
        )
        setAutomations(updatedAutomations)
        localStorage.setItem("automations", JSON.stringify(updatedAutomations))
      }
      
      toast({
        title: active ? "Automation Activated" : "Automation Deactivated",
        description: `The automation has been ${active ? "activated" : "deactivated"}.`,
      })
    } catch (error) {
      console.error("Error toggling automation:", error)
      toast({
        title: "Error",
        description: "Failed to update automation status. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleSaveAutomation = async () => {
    try {
      // Validate required fields
      if (!newAutomation.name || !newAutomation.schedule.startTime || !newAutomation.schedule.endTime || newAutomation.devices.length === 0) {
        toast({
          title: "Missing Information",
          description: "Please fill in all required fields.",
          variant: "destructive",
        })
        return
      }
      
      // Prepare the automation data
      const automationData = {
        ...newAutomation,
        user_id: user.id || user.email,
        household_id: user.householdId
      }
      
      if (editingAutomation && editingAutomation._id) {
        // Update existing automation in backend
        const response = await axios.put(`${API_URL}/api/automations/update/${editingAutomation._id}`, automationData)
        
        // Update local state
        setAutomations(automations.map((automation) =>
          automation._id === editingAutomation._id ? { ...response.data.automation } : automation
        ))
        
        toast({
          title: "Automation Updated",
          description: "Your automation has been successfully updated.",
        })
      } else if (editingAutomation && editingAutomation.id) {
        // Update existing local automation
        const updatedAutomations = automations.map((automation) =>
          automation.id === editingAutomation.id ? { ...newAutomation, id: editingAutomation.id } : automation
        )
        setAutomations(updatedAutomations)
        localStorage.setItem("automations", JSON.stringify(updatedAutomations))
        
        toast({
          title: "Automation Updated",
          description: "Your automation has been successfully updated.",
        })
      } else {
        // Create new automation in backend
        try {
          const response = await axios.post(`${API_URL}/api/automations/create`, automationData)
          
          // Add the new automation to local state
          setAutomations([...automations, response.data.automation])
          
          toast({
            title: "Automation Created",
            description: "Your new automation has been successfully added.",
          })
        } catch (error) {
          console.error("Failed to create automation in backend, falling back to localStorage:", error)
          
          // Fallback to localStorage
          const newAutomationItem = {
            ...newAutomation,
            id: Date.now(),
          }
          const updatedAutomations = [...automations, newAutomationItem]
          setAutomations(updatedAutomations)
          localStorage.setItem("automations", JSON.stringify(updatedAutomations))
          
          toast({
            title: "Automation Created (Local)",
            description: "Your new automation has been saved locally.",
          })
        }
      }
      
      // Close dialog and reset form
      setIsDialogOpen(false)
      setEditingAutomation(null)
      setNewAutomation({
        name: "",
        description: "",
        icon: "Clock",
        active: true,
        schedule: {
          type: "once",
          startTime: "",
          endTime: "",
        },
        devices: [],
      })
    } catch (error) {
      console.error("Error saving automation:", error)
      toast({
        title: "Error",
        description: "Failed to save automation. Please try again.",
        variant: "destructive",
      })
    }
  }

  const handleDeleteAutomation = async (id: string | number) => {
    if (window.confirm("Are you sure you want to delete this automation?")) {
      try {
        if (typeof id === 'string') {
          // Delete from backend
          await axios.delete(`${API_URL}/api/automations/delete/${id}`)
        }
        
        // Update local state regardless of backend or local
        const updatedAutomations = automations.filter((automation) => 
          (automation._id !== id && automation.id !== id)
        )
        setAutomations(updatedAutomations)
        
        // Update localStorage if we're using it
        localStorage.setItem("automations", JSON.stringify(updatedAutomations))
        
        toast({
          title: "Automation Deleted",
          description: "The automation has been successfully removed.",
        })
      } catch (error) {
        console.error("Error deleting automation:", error)
        toast({
          title: "Error",
          description: "Failed to delete automation. Please try again.",
          variant: "destructive",
        })
      }
    }
  }

  const handleEditAutomation = (automation: Automation) => {
    setEditingAutomation(automation)
    setNewAutomation(automation)
    setIsDialogOpen(true)
  }

  const formatSchedule = (schedule: Automation["schedule"]) => {
    if (!schedule || !schedule.type) {
      return "Schedule not set"
    }

    switch (schedule.type) {
      case "once":
        return `Once from ${schedule.startTime} to ${schedule.endTime}`
      case "daily":
        return `Daily from ${schedule.startTime} to ${schedule.endTime}`
      case "weekly":
        return `Weekly on ${schedule.daysOfWeek?.map((day) => daysOfWeek[day]).join(", ")} from ${schedule.startTime} to ${schedule.endTime}`
      case "custom":
        return `Custom schedule from ${schedule.startTime} to ${schedule.endTime}`
      default:
        return "Invalid schedule"
    }
  }

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

  const checkForActiveAutomations = async () => {
    if (!user) return
    
    try {
      const now = new Date()
      const response = await axios.get(`${API_URL}/api/automations/active`, {
        params: {
          user_id: user.id || user.email,
          household_id: user.householdId,
          timestamp: now.toISOString()
        }
      })
      
      if (response.data && response.data.active_automations) {
        const activeAutomations = response.data.active_automations
        
        // Show notifications for newly activated automations
        activeAutomations.forEach((automation: any) => {
          // Check if this automation was activated since our last check
          if (new Date(automation.last_activated) > lastCheckTime) {
            const deviceNames = automation.devices.map((deviceId: string) => {
              const device = devices.find(d => d.id === deviceId)
              return device ? device.name : deviceId
            }).join(", ")
            
            setNotifications(prev => [
              ...prev, 
              `Automation "${automation.name}" activated: ${deviceNames} turned ${automation.action || "on"}`
            ])
            
            // Update device status in our local state
            setDevices(prevDevices => 
              prevDevices.map(device => 
                automation.devices.includes(device.id) 
                  ? { ...device, status: automation.action || "on" } 
                  : device
              )
            )
          }
        })
      }
      
      setLastCheckTime(now)
    } catch (error) {
      console.error("Error checking for active automations:", error)
    }
  }

  useEffect(() => {
    if (!user) return
    
    // Check immediately on load
    checkForActiveAutomations()
    
    // Then check every 30 seconds
    const interval = setInterval(checkForActiveAutomations, 30000)
    
    return () => clearInterval(interval)
  }, [user, devices])

  const removeNotification = (index: number) => {
    setNotifications(prev => prev.filter((_, i) => i !== index))
  }

  // If permission check is still loading or data is loading, show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <NavigationSidebar />
        <div className="flex-1 ml-[72px] flex items-center justify-center">
          <p>Loading automations...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <NavigationSidebar />
      <div className="flex-1 ml-[72px]">
        <motion.div initial="hidden" animate="visible" variants={containerVariants} className="p-6">
          <motion.header variants={itemVariants} className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-2">
              <div className="w-12 h-12 bg-gradient-to-br from-[#FF9500] to-[#FFB800] rounded-full flex items-center justify-center shadow-lg">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Automations</h1>
                <p className="text-sm text-gray-500">Manage your smart home routines</p>
              </div>
            </div>
            {automations.length > 0 && (
              <Button className="bg-[#00B2FF] hover:bg-[#00B2FF]/90" onClick={() => setIsDialogOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                New Automation
              </Button>
            )}
          </motion.header>

          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>{editingAutomation ? "Edit Automation" : "Create New Automation"}</DialogTitle>
                <DialogDescription>
                  {editingAutomation ? "Modify your automation settings." : "Set up a new automation for your smart home."}
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="name" className="text-right">
                    Name
                  </Label>
                  <Input
                    id="name"
                    value={newAutomation.name}
                    onChange={(e) => setNewAutomation({ ...newAutomation, name: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="icon" className="text-right">
                    Icon
                  </Label>
                  <Select
                    value={newAutomation.icon}
                    onValueChange={(value) => setNewAutomation({ ...newAutomation, icon: value })}
                  >
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Select icon" />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.keys(automationIcons).map((icon) => (
                        <SelectItem key={icon} value={icon}>
                          {icon}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="scheduleType" className="text-right">
                    Schedule Type
                  </Label>
                  <Select
                    value={newAutomation.schedule.type}
                    onValueChange={(value: "once" | "daily" | "weekly" | "custom") =>
                      setNewAutomation({
                        ...newAutomation,
                        schedule: { ...newAutomation.schedule, type: value },
                      })
                    }
                  >
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Select schedule type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="once">Once</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="startTime" className="text-right">
                    Start Time
                  </Label>
                  <Input
                    id="startTime"
                    type="time"
                    value={newAutomation.schedule.startTime}
                    onChange={(e) =>
                      setNewAutomation({
                        ...newAutomation,
                        schedule: { ...newAutomation.schedule, startTime: e.target.value },
                      })
                    }
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="endTime" className="text-right">
                    End Time
                  </Label>
                  <Input
                    id="endTime"
                    type="time"
                    value={newAutomation.schedule.endTime}
                    onChange={(e) =>
                      setNewAutomation({
                        ...newAutomation,
                        schedule: { ...newAutomation.schedule, endTime: e.target.value },
                      })
                    }
                    className="col-span-3"
                  />
                </div>
                {newAutomation.schedule.type === "weekly" && (
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label className="text-right">Days</Label>
                    <div className="col-span-3 flex flex-wrap gap-2">
                      {daysOfWeek.map((day, index) => (
                        <div key={day} className="flex items-center space-x-2">
                          <Checkbox
                            id={`day-${index}`}
                            checked={newAutomation.schedule.daysOfWeek?.includes(index)}
                            onCheckedChange={(checked) => {
                              const newDays = checked
                                ? [...(newAutomation.schedule.daysOfWeek || []), index]
                                : newAutomation.schedule.daysOfWeek?.filter((d) => d !== index);
                              setNewAutomation({
                                ...newAutomation,
                                schedule: { ...newAutomation.schedule, daysOfWeek: newDays },
                              });
                            }}
                          />
                          <Label htmlFor={`day-${index}`}>{day}</Label>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="description" className="text-right">
                    Description
                  </Label>
                  <Input
                    id="description"
                    value={newAutomation.description}
                    onChange={(e) => setNewAutomation({ ...newAutomation, description: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 gap-4">
                  <Label className="text-right pt-2">
                    Devices
                  </Label>
                  <div className="col-span-3 border rounded-md p-3 max-h-[200px] overflow-y-auto">
                    {devices.length === 0 ? (
                      <p className="text-sm text-gray-500">No devices available</p>
                    ) : (
                      <div className="space-y-2">
                        {devices.map((device) => (
                          <div key={device.id} className="flex items-center space-x-2">
                            <Checkbox
                              id={`device-${device.id}`}
                              checked={newAutomation.devices.includes(device.id)}
                              onCheckedChange={(checked) => {
                                const updatedDevices = checked
                                  ? [...newAutomation.devices, device.id]
                                  : newAutomation.devices.filter((id) => id !== device.id);
                                setNewAutomation({
                                  ...newAutomation,
                                  devices: updatedDevices,
                                });
                              }}
                            />
                            <Label htmlFor={`device-${device.id}`} className="text-sm flex items-center gap-2">
                              {device.name} <span className="text-gray-500 text-xs">({device.room})</span>
                            </Label>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" onClick={handleSaveAutomation}>
                  {editingAutomation ? "Update automation" : "Save automation"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {automations.length === 0 ? (
              <motion.div variants={itemVariants} className="col-span-full">
                <Card className="bg-white shadow-lg">
                  <CardContent className="p-6 flex flex-col items-center text-center">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                      <Zap className="w-8 h-8 text-blue-500" />
                    </div>
                    <h3 className="text-lg font-semibold mb-2">No Automations Yet</h3>
                    <p className="text-gray-500 mb-4">
                      Create your first automation to start managing your smart home routines.
                    </p>
                    <Button className="bg-[#00B2FF] hover:bg-[#00B2FF]/90" onClick={() => setIsDialogOpen(true)}>
                      <Plus className="w-4 h-4 mr-2" />
                      Add Your First Automation
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ) : (
              automations.map((automation) => (
                <motion.div key={automation._id || automation.id} variants={itemVariants}>
                  <Card className={`overflow-hidden ${automation.active ? "" : "opacity-50"}`}>
                    <CardHeader
                      className={`${automation.active ? "bg-gradient-to-r from-[#00B2FF] to-[#0085FF]" : "bg-gray-400"} text-white`}
                    >
                      <CardTitle className="flex items-center justify-between">
                        <span>{automation.name}</span>
                        <Switch
                          checked={automation.active}
                          onCheckedChange={(checked) => handleToggleAutomation(automation._id || automation.id!, checked)}
                        />
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-4 mb-4">
                        <div className={`p-2 rounded-full ${automation.active ? "bg-blue-100" : "bg-gray-200"}`}>
                          {automation.icon &&
                            automationIcons[automation.icon] &&
                            React.createElement(automationIcons[automation.icon], {
                              className: `w-6 h-6 ${automation.active ? "text-blue-600" : "text-gray-600"}`,
                            })}
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">{automation.description}</p>
                          <div className="flex items-center space-x-2 mt-1">
                            <Repeat className="w-4 h-4 text-gray-400" />
                            <span className="text-xs text-gray-500">{formatSchedule(automation.schedule)}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <Badge variant="outline" className="text-blue-600 border-blue-600">
                              {automation.devices.length} {automation.devices.length === 1 ? 'device' : 'devices'}
                            </Badge>
                            {automation.devices.length > 0 && (
                              <button 
                                className="ml-2 text-xs text-blue-500 hover:underline focus:outline-none"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setExpandedDeviceLists(prev => ({
                                    ...prev,
                                    [`${automation._id || automation.id}`]: !prev[`${automation._id || automation.id}`]
                                  }))
                                }}
                              >
                                {expandedDeviceLists[`${automation._id || automation.id}`] ? 'Hide' : 'Show'} details
                              </button>
                            )}
                          </div>
                          <div className="flex space-x-2">
                            <Button variant="outline" size="sm" onClick={() => handleEditAutomation(automation)}>
                              <Edit className="w-4 h-4 text-blue-500" />
                            </Button>
                            <Button variant="outline" size="sm" onClick={() => handleDeleteAutomation(automation._id || automation.id!)}>
                              <Trash2 className="w-4 h-4 text-red-500" />
                            </Button>
                          </div>
                        </div>
                        {expandedDeviceLists[`${automation._id || automation.id}`] && (
                          <div className="text-xs text-gray-600 pl-1 mt-2">
                            {automation.devices.map(deviceId => {
                              const device = devices.find(d => d.id === deviceId);
                              return device ? (
                                <div key={deviceId} className="flex items-center mt-1">
                                  <div className={`w-2 h-2 rounded-full mr-1 ${device.status === 'on' ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                                  <span>{device.name} <span className="text-gray-400">({device.room})</span></span>
                                </div>
                              ) : (
                                <div key={deviceId} className="mt-1">Unknown device</div>
                              );
                            })}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))
            )}
          </motion.div>
        </motion.div>
        {notifications.map((message, index) => (
          <AutomationNotification 
            key={index} 
            message={message} 
            onClose={() => removeNotification(index)} 
          />
        ))}
      </div>
    </div>
  )
}