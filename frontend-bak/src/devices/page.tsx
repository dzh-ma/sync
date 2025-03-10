"use client"

import React from "react"
import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/card"
import { Button } from "../../components/ui/button"
import { Switch } from "../../components/ui/switch"
import { Slider } from "../../components/ui/slider"
import { Lightbulb, Thermometer, Fan, Tv, Lock, Plus, Smartphone, Edit, Trash2 } from "lucide-react"
import Link from "next/link"
import { motion } from "framer-motion"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "../../components/ui/dialog"
import { Label } from "../../components/ui/label"
import { Input } from "../../components/ui/input"
import { NavigationSidebar } from "../../components/navigation-sidebar"; // Import the navbar



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
  totalEnergyConsumed?: number
  lastStatusChange?: number
}

const deviceIcons = {
  light: Lightbulb,
  thermostat: Thermometer,
  fan: Fan,
  tv: Tv,
  lock: Lock,
}

const Icon = ({ type }: { type: string }) => {
  const IconComponent = deviceIcons[type as keyof typeof deviceIcons] || null
  return <IconComponent className="h-6 w-6" />
}

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([])
  const [editingDevice, setEditingDevice] = useState<Device | null>(null)

  useEffect(() => {
    const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]")
    setDevices(storedDevices)
  }, [])

  const updateDevice = (id: string, updates: Partial<Device>) => {
    const updatedDevices = devices.map((device) => {
      if (device.id === id) {
        const newDevice = { ...device, ...updates }

        if (updates.status !== undefined && updates.status !== device.status) {
          const now = Date.now()
          const timeOn = (now - (device.lastStatusChange || now)) / (1000 * 60 * 60) // hours
          if (device.status === "on") {
            newDevice.totalEnergyConsumed =
              (newDevice.totalEnergyConsumed || 0) + ((device.powerConsumption || 0) / 1000) * timeOn
          }
          newDevice.lastStatusChange = now
        }

        return newDevice
      }
      return device
    })
    setDevices(updatedDevices)
    localStorage.setItem("devices", JSON.stringify(updatedDevices))
  }

  const deleteDevice = (id: string) => {
    if (window.confirm("Are you sure you want to delete this device?")) {
      const updatedDevices = devices.filter((device) => device.id !== id)
      setDevices(updatedDevices)
      localStorage.setItem("devices", JSON.stringify(updatedDevices))
    }
  }

  const handleEditDevice = (device: Device) => {
    setEditingDevice(device)
  }

  const saveEditedDevice = () => {
    if (editingDevice) {
      const updatedDevices = devices.map((device) => (device.id === editingDevice.id ? editingDevice : device))
      setDevices(updatedDevices)
      localStorage.setItem("devices", JSON.stringify(updatedDevices))
      setEditingDevice(null)
    }
  }

  const renderDeviceControls = (device: Device) => {
    switch (device.type) {
      case "light":
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Power</span>
              <Switch
                checked={device.status === "on"}
                onCheckedChange={(checked) => updateDevice(device.id, { status: checked ? "on" : "off" })}
              />
            </div>
            {device.status === "on" && (
              <div className="space-y-2">
                <span>Brightness</span>
                <Slider
                  value={[device.brightness || 100]}
                  onValueChange={([value]) => updateDevice(device.id, { brightness: value })}
                  max={100}
                  step={1}
                />
              </div>
            )}
          </div>
        )
      case "thermostat":
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Power</span>
              <Switch
                checked={device.status === "on"}
                onCheckedChange={(checked) => updateDevice(device.id, { status: checked ? "on" : "off" })}
              />
            </div>
            {device.status === "on" && (
              <div className="space-y-2">
                <span>Temperature (°C)</span>
                <Slider
                  value={[device.temperature || 22]}
                  onValueChange={([value]) => updateDevice(device.id, { temperature: value })}
                  min={16}
                  max={30}
                  step={0.5}
                />
              </div>
            )}
          </div>
        )
      case "fan":
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Power</span>
              <Switch
                checked={device.status === "on"}
                onCheckedChange={(checked) => updateDevice(device.id, { status: checked ? "on" : "off" })}
              />
            </div>
            {device.status === "on" && (
              <div className="space-y-2">
                <span>Speed</span>
                <Slider
                  value={[device.speed || 1]}
                  onValueChange={([value]) => updateDevice(device.id, { speed: value })}
                  min={1}
                  max={5}
                  step={1}
                />
              </div>
            )}
          </div>
        )
      default:
        return (
          <div className="flex items-center justify-between">
            <span>Power</span>
            <Switch
              checked={device.status === "on"}
              onCheckedChange={(checked) => updateDevice(device.id, { status: checked ? "on" : "off" })}
            />
          </div>
        )
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <NavigationSidebar /> {/* Add the navbar here */}
      <div className="flex-1 ml-[72px]">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="p-6"
        >
          <motion.header
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex justify-between items-center mb-6"
          >
            <div className="flex items-center gap-2">
              <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                <Smartphone className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Devices</h1>
                <p className="text-sm text-gray-500">Manage and control your smart devices</p>
              </div>
            </div>
            {devices.length > 0 && (
              <Link href="/add-device">
                <Button className="bg-[#00B2FF] hover:bg-[#00B2FF]/90">
                  <Plus className="mr-2 h-4 w-4" /> Add Device
                </Button>
              </Link>
            )}
          </motion.header>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
          >
            {devices.length === 0 ? (
              <Card className="col-span-full p-6 text-center">
                <div className="flex flex-col items-center justify-center space-y-4">
                  <div className="rounded-full bg-blue-100 p-3">
                    <Smartphone className="h-8 w-8 text-[#00B2FF]" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-semibold text-lg">No devices added yet</h3>
                    <p className="text-muted-foreground">Get started by adding your first smart device</p>
                  </div>
                  <Link href="/add-device">
                    <Button className="bg-[#00B2FF] hover:bg-[#00B2FF]/90">
                      <Plus className="mr-2 h-4 w-4" /> Add Your First Device
                    </Button>
                  </Link>
                </div>
              </Card>
            ) : (
              devices.map((device) => (
                <motion.div
                  key={device.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Card className="overflow-hidden">
                    <CardHeader className="bg-gradient-to-r from-[#00B2FF] to-[#0085FF] text-white p-4">
                      <CardTitle className="flex items-center justify-between">
                        <span className="text-lg font-semibold">{device.name}</span>
                        <Icon type={device.type} />
                      </CardTitle>
                      <p className="text-sm opacity-80">{device.room}</p>
                    </CardHeader>
                    <CardContent className="p-4">
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-500">Status</span>
                          <span
                            className={`text-sm font-medium ${device.status === "on" ? "text-green-500" : "text-red-500"}`}
                          >
                            {device.status === "on" ? "On" : "Off"}
                          </span>
                        </div>
                        {renderDeviceControls(device)}
                        {device.powerConsumption && (
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-500">Power Consumption</span>
                            <span className="font-medium">{device.powerConsumption} W</span>
                          </div>
                        )}
                        {device.totalEnergyConsumed && (
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-500">Total Energy Consumed</span>
                            <span className="font-medium">{device.totalEnergyConsumed.toFixed(2)} kWh</span>
                          </div>
                        )}
                        <div className="flex justify-end space-x-2 mt-4">
                          <Button variant="outline" size="sm" onClick={() => handleEditDevice(device)}>
                            <Edit className="w-4 h-4" />
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => deleteDevice(device.id)}>
                            <Trash2 className="w-4 h-4" />
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
  )
}
