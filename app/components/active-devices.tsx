"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Lightbulb, Thermometer, Fan, Tv, Maximize2, Minimize2, Lock } from "lucide-react"
import styles from './ActiveDevices.module.css'
import { toast } from "@/components/ui/use-toast"
import axios from "axios"

// Set API URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

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

const deviceIcons: Record<string, any> = {
  light: Lightbulb,
  thermostat: Thermometer,
  fan: Fan,
  tv: Tv,
}

export function ActiveDevices() {
  const [devices, setDevices] = useState<Device[]>([])
  const [isMaximized, setIsMaximized] = useState(false)
  const [hasDeviceControl, setHasDeviceControl] = useState(true)
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    // Mark component as mounted on client
    setIsMounted(true)
    
    // Only run this code on the client side
    if (typeof window !== 'undefined') {
      // Load devices
      const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]") as Device[]
      setDevices(storedDevices)
      
      // Check permissions
      const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}")
      const currentMember = JSON.parse(localStorage.getItem("currentMember") || "{}")
      
      // Determine if the user has device control permission
      const permissions = currentUser.permissions || currentMember.permissions || {}
      setHasDeviceControl(permissions.deviceControl === true)
      
      // Add event listener for local storage changes from other components
      const handleStorageChange = (e: StorageEvent) => {
        if (e.key === "devices") {
          try {
            const newDevices = JSON.parse(e.newValue || "[]");
            setDevices(newDevices);
          } catch (error) {
            console.error("Error parsing updated devices:", error);
          }
        }
      };
      
      window.addEventListener("storage", handleStorageChange);
      
      // Cleanup
      return () => {
        window.removeEventListener("storage", handleStorageChange);
      };
    }
  }, [])

  const toggleDevice = async (id: string) => {
    // Check permission before allowing toggle
    if (!hasDeviceControl) {
      toast({
        title: "Permission Denied",
        description: "You don't have permission to control devices.",
        variant: "destructive",
      })
      return
    }
    
    try {
      // Find the device to toggle
      const deviceToToggle = devices.find(d => d.id === id);
      if (!deviceToToggle) {
        console.error(`Device with ID ${id} not found`);
        return;
      }
      
      // Calculate the new status
      const newStatus = deviceToToggle.status === "on" ? "off" : "on" as "on" | "off";
      
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
      
      // Calculate energy consumed if turning off
      let energyConsumed = 0;
      if (deviceToToggle.status === "on" && newStatus === "off" && deviceToToggle.lastStatusChange) {
        const timeOn = (Date.now() - deviceToToggle.lastStatusChange) / 1000 / 3600; // hours
        energyConsumed = (deviceToToggle.basePowerConsumption || 0) * timeOn / 1000; // kWh
        console.log(`Device ${deviceToToggle.name} consumed ${energyConsumed.toFixed(4)} kWh over ${timeOn.toFixed(2)} hours`);
        
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
      const updatedDevices = devices.map(device => {
        if (device.id === id) {
          return {
            ...device,
            status: newStatus,
            lastStatusChange: Date.now(),
            totalEnergyConsumed: (device.totalEnergyConsumed || 0) + energyConsumed
          };
        }
        return device;
      });
      
      setDevices(updatedDevices);
      
      // Get all devices from localStorage to avoid updating just the visible ones
      const allStoredDevices = JSON.parse(localStorage.getItem("devices") || "[]") as Device[];
      
      // Update all devices in localStorage
      const updatedStoredDevices = allStoredDevices.map(device => {
        if (device.id === id || device.name === deviceToToggle.name) {
          return {
            ...device,
            status: newStatus,
            lastStatusChange: Date.now(),
            totalEnergyConsumed: (device.totalEnergyConsumed || 0) + energyConsumed
          };
        }
        return device;
      });
      
      localStorage.setItem("devices", JSON.stringify(updatedStoredDevices));
      
      // Now update in the backend
      try {
        // Use fetch API instead of axios for consistency
        const response = await fetch(`${API_URL}/api/user/toggle-device?user_id=${encodeURIComponent(userId || '')}&device_name=${encodeURIComponent(deviceToToggle.name)}&household_id=${encodeURIComponent(householdId || '')}&status=${newStatus}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
        });
        
        if (!response.ok) {
          throw new Error(`Error toggling device: ${response.statusText}`);
        }
        
        const responseData = await response.json();
        console.log("Device toggle successful:", responseData);
        
        toast({
          title: `Device ${newStatus === "on" ? "On" : "Off"}`,
          description: `${deviceToToggle.name} is now ${newStatus}.`,
        });
        
        // Trigger statistics collection after a short delay
        // This ensures the backend has time to process the device state change
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
              
              // Navigate to statistics page if on dashboard
              const currentPath = window.location.pathname;
              if (currentPath === '/dashboard') {
                // Optionally refresh stats on dashboard
                // window.dispatchEvent(new CustomEvent('refreshDashboardStats'));
              }
            } else {
              console.warn("Failed to trigger statistics collection after toggle");
            }
          } catch (statsError) {
            console.error("Error triggering statistics collection:", statsError);
          }
        }, 1000); // Wait 1 second to ensure database has registered the change
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
      
      // Refresh from localStorage in case of error
      const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]");
      setDevices(storedDevices);
    }
  }

  // Show a placeholder during server rendering to prevent hydration mismatch
  if (!isMounted) {
    return (
      <Card className={`h-full`}>
        <CardHeader>
          <CardTitle>Active Devices</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-muted-foreground">Loading devices...</div>
        </CardContent>
      </Card>
    )
  }

  if (!hasDeviceControl) {
    return (
      <Card className={`${isMaximized ? styles.cardMaximizedA : ""} h-full`}>
        <CardHeader className={styles.cardTitleA}>
          <CardTitle>Active Devices</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center justify-center p-6">
          <Lock className="w-12 h-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-semibold mb-2">Access Required</h3>
          <p className="text-sm text-gray-500 text-center mb-4">
            You don't have permission to view or control devices.
          </p>
        </CardContent>
      </Card>
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
