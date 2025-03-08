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
import { NavigationSidebar } from "@/app/components/navigation-sidebar"; // Import the navbar


interface Automation {
  id: number
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
}

interface Device {
  id: string
  name: string
  type: string
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
  const [automations, setAutomations] = useState<Automation[]>([])
  const [devices, setDevices] = useState<Device[]>([])
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingAutomation, setEditingAutomation] = useState<Automation | null>(null)
  const [newAutomation, setNewAutomation] = useState<Automation>({
    id: 0,
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

  useEffect(() => {
    const storedAutomations = JSON.parse(localStorage.getItem("automations") || "[]")
    setAutomations(storedAutomations)
    const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]")
    setDevices(storedDevices)
  }, [])

  const handleToggleAutomation = (id: number, active: boolean) => {
    const updatedAutomations = automations.map((automation) =>
      automation.id === id ? { ...automation, active } : automation,
    )
    setAutomations(updatedAutomations)
    localStorage.setItem("automations", JSON.stringify(updatedAutomations))
  }

  const handleSaveAutomation = () => {
    if (editingAutomation) {
      const updatedAutomations = automations.map((automation) =>
        automation.id === editingAutomation.id ? { ...newAutomation, id: editingAutomation.id } : automation,
      )
      setAutomations(updatedAutomations)
      localStorage.setItem("automations", JSON.stringify(updatedAutomations))
      toast({
        title: "Automation Updated",
        description: "Your automation has been successfully updated.",
      })
    } else {
      const newAutomationItem = {
        ...newAutomation,
        id: Date.now(),
      }
      const updatedAutomations = [...automations, newAutomationItem]
      setAutomations(updatedAutomations)
      localStorage.setItem("automations", JSON.stringify(updatedAutomations))
      toast({
        title: "Automation Created",
        description: "Your new automation has been successfully added.",
      })
    }
    setIsDialogOpen(false)
    setEditingAutomation(null)
    setNewAutomation({
      id: 0,
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
  }

  const handleDeleteAutomation = (id: number) => {
    if (window.confirm("Are you sure you want to delete this automation?")) {
      const updatedAutomations = automations.filter((automation) => automation.id !== id)
      setAutomations(updatedAutomations)
      localStorage.setItem("automations", JSON.stringify(updatedAutomations))
      toast({
        title: "Automation Deleted",
        description: "The automation has been successfully removed.",
      })
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
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="devices" className="text-right">
                    Devices
                  </Label>
                  <Select
                    value={newAutomation.devices[0] || ""}
                    onValueChange={(value) => setNewAutomation({ ...newAutomation, devices: [value] })}
                  >
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Select device" />
                    </SelectTrigger>
                    <SelectContent>
                      {devices.map((device) => (
                        <SelectItem key={device.id} value={device.id}>
                          {device.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
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
                <motion.div key={automation.id} variants={itemVariants}>
                  <Card className={`overflow-hidden ${automation.active ? "" : "opacity-50"}`}>
                    <CardHeader
                      className={`${automation.active ? "bg-gradient-to-r from-[#00B2FF] to-[#0085FF]" : "bg-gray-400"} text-white`}
                    >
                      <CardTitle className="flex items-center justify-between">
                        <span>{automation.name}</span>
                        <Switch
                          checked={automation.active}
                          onCheckedChange={(checked) => handleToggleAutomation(automation.id, checked)}
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
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className="text-blue-600 border-blue-600">
                          {automation.devices.length} devices
                        </Badge>
                        <div className="flex space-x-2">
                          <Button variant="outline" size="sm" onClick={() => handleEditAutomation(automation)}>
                            <Edit className="w-4 h-4 text-blue-500" />
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => handleDeleteAutomation(automation.id)}>
                            <Trash2 className="w-4 h-4 text-red-500" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))
            )}
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}