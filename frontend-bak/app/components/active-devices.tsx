"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Lightbulb, Thermometer, Fan, Tv, Maximize2, Minimize2 } from "lucide-react"
import styles from './ActiveDevices.module.css'

interface Device {
  id: string
  name: string
  type: string
  room: string
  status: "on" | "off"
}

const deviceIcons: Record<string, any> = {
  light: Lightbulb,
  thermostat: Thermometer,
  fan: Fan,
  tv: Tv,
}

export function ActiveDevices() {
  const [devices, setDevices] = useState<Device[]>([])
  const [isMaximized, setIsMaximized] = useState(false)

  useEffect(() => {
    const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]")
    setDevices(storedDevices)
  }, [])

  const toggleDevice = (id: string) => {
    setDevices(
      devices.map((device) => {
        if (device.id === id) {
          const updatedDevice = {
            ...device,
            status: device.status === "on" ? "off" : "on",
          }
          // Update in localStorage
          const allDevices = JSON.parse(localStorage.getItem("devices") || "[]")
          const updatedDevices = allDevices.map((d: Device) => (d.id === id ? updatedDevice : d))
          localStorage.setItem("devices", JSON.stringify(updatedDevices))
          return updatedDevice
        }
        return device
      }),
    )
  }

  return (
    <Card className={`${isMaximized ? styles.cardMaximizedA : ""} h-full`}>
      <CardHeader className={styles.cardTitleA}>
        <CardTitle>Active Devices</CardTitle>
        <Button variant="ghost" size="sm" onClick={() => setIsMaximized(!isMaximized)}>
          {isMaximized ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
        </Button>
      </CardHeader>
      <CardContent>
        <div className={styles.deviceListA}>
          {devices.length === 0 ? (
            <p className="text-sm text-muted-foreground">No devices added yet</p>
          ) : (
            devices.slice(0, isMaximized ? devices.length : 4).map((device) => {
              const Icon = deviceIcons[device.type] || Lightbulb
              return (
                <div key={device.id} className={styles.deviceItemA}>
                  <div className="flex items-center space-x-4">
                    <div
                      className={`${styles.deviceIconWrapperA} ${device.status === "on" ? styles.deviceIconOn : styles.deviceIconOff}`}
                    >
                      <Icon className={`${styles.deviceIconA} ${device.status === "on" ? "text-[#00B2FF]" : "text-gray-500"}`} />
                    </div>
                    <div>
                      <p className={styles.deviceNameA}>{device.name}</p>
                      <p className={styles.deviceRoomA}>{device.room}</p>
                    </div>
                  </div>
                  <Switch
                    checked={device.status === "on"}
                    onCheckedChange={() => toggleDevice(device.id)}
                    className={styles.deviceStatusSwitchA}
                  />
                </div>
              )
            })
          )}
        </div>
      </CardContent>
    </Card>
  )
}
