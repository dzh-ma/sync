"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Lightbulb, Thermometer, Fan, Tv, Lock, Plus, Smartphone, Edit, Trash2 } from "lucide-react"
import Link from "next/link"
import { motion } from "framer-motion"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { useToast } from "@/components/ui/use-toast"
import { NavigationSidebar } from "@/app/components/navigation-sidebar"
import axios from "axios"
import { v4 as uuidv4 } from "uuid"
import useEnergySync from "@/app/hooks/useEnergySync"

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  usageHistory?: {
    startTime: number
    endTime?: number
    powerConsumption: number
    energyConsumed: number
  }[]
}

const deviceIcons = {
    light: Lightbulb,
    thermostat: Thermometer,
    fan: Fan,
    tv: Tv,
    lock: Lock,
    smartphone: Smartphone,
    plug: () => (
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
            <path d="M12 22v-5" />
            <path d="M9 8V2" />
            <path d="M15 8V2" />
            <path d="M18 8v4a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8Z" />
        </svg>
    ),
    coffee_maker: () => (
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
            <path d="M17 8h1a4 4 0 1 1 0 8h-1" />
            <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z" />
            <line x1="6" y1="2" x2="6" y2="4" />
            <line x1="10" y1="2" x2="10" y2="4" />
            <line x1="14" y1="2" x2="14" y2="4" />
        </svg>
    ),
    refrigerator: () => (
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
            <path d="M5 6a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6Z" />
            <path d="M5 10h14" />
            <path d="M15 7v6" />
        </svg>
    ),
}

// Base power consumption values for different device types
const BASE_POWER_CONSUMPTION: Record<string, number> = {
  light: 8.5, // watts
  thermostat: 1500, // watts
  fan: 60, // watts
  tv: 100, // watts
  lock: 5, // watts
}

// Calculate power consumption based on device type and settings
const calculatePowerConsumption = (device: Device): number => {
  // Use the device's specific basePowerConsumption value
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
}

const Icon = ({ type }: { type: string }) => {
  const IconComponent = deviceIcons[type as keyof typeof deviceIcons] || Smartphone
  return <IconComponent className="h-6 w-6" />
}

const generateRandomPowerConsumption = (deviceType: string) => {
  const ranges = {
    light: [5, 60],               // LED to incandescent bulbs
    thermostat: [100, 3500],      // Small to large HVAC systems
    fan: [10, 120],               // Small desk fan to ceiling fan
    tv: [30, 200],                // Small LED TV to large plasma TV
    lock: [2, 10],                // Smart locks use very little power
    plug: [0, 5],                 // Smart plug itself uses minimal power
    coffee_maker: [600, 1500],    // Small to large coffee makers
    microwave: [600, 1200],       // Compact to full-size microwaves
    refrigerator: [100, 400],     // Mini fridge to large refrigerator
    washing_machine: [350, 800],  // Energy-efficient to standard models
  };
  
  const range = ranges[deviceType as keyof typeof ranges] || [1, 10];
  const [min, max] = range;
  return parseFloat((Math.random() * (max - min) + min).toFixed(1));
};

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([])
  const [editingDevice, setEditingDevice] = useState<Device | null>(null)
  const { toast } = useToast()
  const { syncEnergyConsumption } = useEnergySync()

    useEffect(() => {
        const fetchDevices = async () => {
      try {
        // Get user info first
        const storedUser = localStorage.getItem("currentUser");
        const storedMember = localStorage.getItem("currentMember");
        
        let userId: string | undefined = undefined;
        let householdId: string | undefined = undefined;
        
        if (storedUser) {
          const currentUser = JSON.parse(storedUser);
          userId = currentUser.id;
          householdId = currentUser.householdId;
        } else if (storedMember) {
          const currentMember = JSON.parse(storedMember);
          userId = currentMember.id;
          householdId = currentMember.householdId;
        }
        
        if (!userId) {
          console.error("No user ID found");
          // Use localStorage devices as fallback only if no user ID
          const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]");
          setDevices(storedDevices);
          return;
        }
        
        // First try to fetch from backend - prioritize backend data over localStorage
        try {
          const response = await axios.get(`${API_URL}/api/user/devices`, {
            params: {
              user_id: userId,
              household_id: householdId || ''
            }
          });
          
          const backendDevices = response.data || [];
          console.log("Backend devices:", backendDevices);
          
          // As a fallback, get devices from localStorage
          const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]");
          
          // Create a map of stored devices by name for quick lookup
          const deviceMap = new Map();
          storedDevices.forEach((device: Device) => {
            deviceMap.set(device.name, device);
          });
          
          // Process and merge devices from backend
          const mergedDevices: Device[] = [];
          
          backendDevices.forEach((backendDevice: any) => {
            const deviceName = backendDevice.name;
            const existingDevice = deviceMap.get(deviceName);
            
            // Get the base power consumption from backend or generate a new one
            const basePowerConsumption = 
                backendDevice.base_power_consumption || 
                (existingDevice?.basePowerConsumption) || 
                generateRandomPowerConsumption(backendDevice.type);
                
            console.log(`Device ${deviceName} (${backendDevice.type}): basePowerConsumption = ${basePowerConsumption}`);
            
            // Add device with backend status as priority
            mergedDevices.push({
              id: existingDevice?.id || `${backendDevice.type}-${Date.now()}`,
              name: deviceName,
              type: backendDevice.type,
              room: backendDevice.room,
              status: (backendDevice.status || "off") as "on" | "off",
              basePowerConsumption: basePowerConsumption,
              powerConsumption: backendDevice.status === "on" ? basePowerConsumption : 0,
              totalEnergyConsumed: backendDevice.total_energy_consumed || 0,
              lastStatusChange: backendDevice.last_status_change ? 
                new Date(backendDevice.last_status_change).getTime() : Date.now(),
              brightness: backendDevice.settings?.brightness || existingDevice?.brightness,
              temperature: backendDevice.settings?.temperature || existingDevice?.temperature,
              speed: backendDevice.settings?.speed || existingDevice?.speed,
            });
            
            // Remove this device from the map so we know it's been processed
            deviceMap.delete(deviceName);
          });
          
          // If there are any devices in localStorage that aren't in the backend,
          // we'll add them to our merged list as well for a comprehensive view
          deviceMap.forEach((device: Device) => {
            mergedDevices.push(device);
          });
          
          // Update state and localStorage with merged devices
          setDevices(mergedDevices);
          localStorage.setItem("devices", JSON.stringify(mergedDevices));
          
          // Force synchronization with backend for energy consumption values
          await syncEnergyConsumption();
          
        } catch (error) {
          console.error("Error fetching from backend:", error);
          // Fall back to localStorage devices if backend fails
          const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]");
          setDevices(storedDevices);
        }
      } catch (error) {
        console.error("Error in fetchDevices:", error);
      }
    }
    
    // Initial fetch
    fetchDevices();
    
    // Set up periodic refresh for device data and energy consumption
    const refreshInterval = setInterval(() => {
      fetchDevices();
    }, 60000); // Refresh every 60 seconds
    
    // Clean up interval on component unmount
    return () => clearInterval(refreshInterval);
  }, [syncEnergyConsumption])

  const toggleDevice = async (id: string) => {
    try {
      const deviceToUpdate = devices.find((d) => d.id === id);
      if (!deviceToUpdate) return;
      
      const newStatus = deviceToUpdate.status === "on" ? "off" : "on";
      
      // Get user info from localStorage
      const storedUser = localStorage.getItem("currentUser");
      const storedMember = localStorage.getItem("currentMember");
      
      let userId: string | undefined = undefined;
      let householdId: string | undefined = undefined;
      
      if (storedUser) {
        const currentUser = JSON.parse(storedUser);
        userId = currentUser.id;
        householdId = currentUser.householdId;
      } else if (storedMember) {
        const currentMember = JSON.parse(storedMember);
        userId = currentMember.id;
        householdId = currentMember.householdId;
      }
      
      if (!userId) {
        console.error("No user ID found");
        toast({
          title: "Error",
          description: "User information not found. Please login again.",
          variant: "destructive",
        });
        return;
      }
      
      // Calculate energy consumed if turning off
      let energyConsumed = 0;
      if (deviceToUpdate.status === "on" && deviceToUpdate.lastStatusChange) {
        const timeOn = (Date.now() - deviceToUpdate.lastStatusChange) / 1000 / 3600; // hours
        energyConsumed = (deviceToUpdate.powerConsumption || 0) * timeOn / 1000; // kWh
        console.log(`Device ${deviceToUpdate.name} consumed ${energyConsumed.toFixed(4)} kWh over ${timeOn.toFixed(2)} hours`);
        
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
              userId,
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
      
      // Calculate new power consumption based on status and device settings
      const newPowerConsumption = newStatus === "on" 
        ? calculatePowerConsumption(deviceToUpdate) 
        : 0;
        
      // Update local state first for responsive UI
      // Create updated device object
      const updatedDevice: Device = {
        ...deviceToUpdate,
        status: newStatus as "on" | "off",
        powerConsumption: newPowerConsumption,
        totalEnergyConsumed: (deviceToUpdate.totalEnergyConsumed || 0) + energyConsumed,
        lastStatusChange: Date.now(),
      };
      
      // Update in state - create a new array with the updated device
      const newDevices = devices.map(device => 
        device.id === id ? updatedDevice : device
      );
      
      // Update state
      setDevices(newDevices);
      
      // Update in localStorage for persistence
      const allStoredDevices = JSON.parse(localStorage.getItem("devices") || "[]");
      
      // Update all matching devices in localStorage (by id or name to catch all instances)
      const updatedStoredDevices = allStoredDevices.map((device: any) => {
        if (device.id === id || device.name === deviceToUpdate.name) {
          return {
            ...device,
            status: newStatus,
            powerConsumption: newPowerConsumption,
            totalEnergyConsumed: (device.totalEnergyConsumed || 0) + energyConsumed,
            lastStatusChange: Date.now(),
          };
        }
        return device;
      });
      
      localStorage.setItem("devices", JSON.stringify(updatedStoredDevices));
      
      // Call API to update backend
      try {
        // Toggle the device via API
        const response = await fetch(`${API_URL}/api/user/toggle-device?user_id=${encodeURIComponent(userId || '')}&device_name=${encodeURIComponent(deviceToUpdate.name)}&household_id=${encodeURIComponent(householdId || '')}&status=${newStatus}`, {
          method: "PUT",
        });
        
        if (!response.ok) {
          throw new Error(`Failed to toggle device: ${response.statusText}`);
        }
        
        const responseData = await response.json();
        console.log("Device toggle response:", responseData);
        
        // Show toast notification for user feedback
        toast({
          title: `Device ${newStatus === "on" ? "On" : "Off"}`,
          description: `${deviceToUpdate.name} is now ${newStatus}.`,
        });
        
        // Trigger statistics collection again AFTER toggling
        // This ensures the new device state is also recorded
        setTimeout(async () => {
          try {
            console.log("Triggering statistics collection after device toggle");
            const statsResponse = await fetch(`/api/statistics/collect`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                userId,
                householdId: householdId || ''
              }),
            });
            
            if (statsResponse.ok) {
              console.log("Statistics collection triggered successfully after toggle");
              
              // Fetch the latest energy consumption data after toggle
              setTimeout(async () => {
                try {
                  // Use the energy sync hook to update all devices
                  await syncEnergyConsumption();
                  console.log(`Updated energy consumption for ${deviceToUpdate.name} from backend`);
                } catch (error) {
                  console.error("Error updating energy consumption after toggle:", error);
                }
              }, 2000); // Wait 2 seconds after stats collection to ensure data is updated
            } else {
              console.warn("Failed to trigger statistics collection after toggle");
            }
          } catch (statsError) {
            console.error("Error triggering statistics collection:", statsError);
          }
        }, 1000); // Wait 1 second to ensure database has registered the device state change
        
      } catch (error) {
        console.error("Error toggling device:", error);
        toast({
          title: "Error",
          description: "Failed to sync device status with server. Local changes applied.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Error in toggleDevice:", error);
      toast({
        title: "Error",
        description: "Something went wrong. Please try again.",
        variant: "destructive",
      });
    }
  };

  const updateBrightness = async (id: string, brightness: number) => {
    try {
      const deviceToUpdate = devices.find((d) => d.id === id);
      if (!deviceToUpdate) return;
      
      // Get user info
      const storedUser = localStorage.getItem("currentUser");
      const storedMember = localStorage.getItem("currentMember");
      
      let userId: string | undefined = undefined;
      let householdId: string | undefined = undefined;
      
      if (storedUser) {
        const currentUser = JSON.parse(storedUser);
        userId = currentUser.id;
        householdId = currentUser.householdId;
      } else if (storedMember) {
        const currentMember = JSON.parse(storedMember);
        userId = currentMember.id;
        householdId = currentMember.householdId;
      }
      
      if (!userId) {
        console.error("No user ID found");
        return;
      }
      
      // Calculate new power consumption based on updated brightness
      const updatedDevice = {...deviceToUpdate, brightness};
      const calculatedPower = calculatePowerConsumption(updatedDevice);
      
      // Update in backend - using POST instead of PUT
      await axios.post(`${API_URL}/api/user/update-device-settings`, {
        user_id: userId,
        household_id: householdId,
        device_name: deviceToUpdate.name,
        settings: {
          brightness: brightness
        },
        calculated_power: calculatedPower // Send calculated power to backend
      });
      
      // Update in state
      setDevices(
        devices.map((device) => {
          if (device.id === id) {
            const updatedDevice = {
              ...device,
              brightness,
              powerConsumption: device.status === "on" ? 
                calculatedPower : 0,
              basePowerConsumption: device.basePowerConsumption // Preserve base power
            };
            return updatedDevice;
          }
          return device;
        })
      );
      
      // Update in localStorage
      localStorage.setItem(
        "devices",
        JSON.stringify(
          devices.map((device) => {
            if (device.id === id) {
              return {
                ...device,
                brightness,
                powerConsumption: device.status === "on" ? 
                  calculatedPower : 0,
                basePowerConsumption: device.basePowerConsumption // Preserve base power
              };
            }
            return device;
          })
        )
      );
    } catch (error) {
      console.error("Error updating brightness:", error);
      toast({
        title: "Error",
        description: "Failed to update brightness. Please try again.",
        variant: "destructive",
      });
    }
  };

  const updateTemperature = async (id: string, temperature: number) => {
    try {
      const deviceToUpdate = devices.find((d) => d.id === id);
      if (!deviceToUpdate) return;
      
      // Get user info
      const storedUser = localStorage.getItem("currentUser");
      const storedMember = localStorage.getItem("currentMember");
      
      let userId: string | undefined = undefined;
      let householdId: string | undefined = undefined;
      
      if (storedUser) {
        const currentUser = JSON.parse(storedUser);
        userId = currentUser.id;
        householdId = currentUser.householdId;
      } else if (storedMember) {
        const currentMember = JSON.parse(storedMember);
        userId = currentMember.id;
        householdId = currentMember.householdId;
      }
      
      if (!userId) {
        console.error("No user ID found");
        return;
      }
      
      // Calculate new power consumption based on updated temperature
      const updatedDevice = {...deviceToUpdate, temperature};
      const calculatedPower = calculatePowerConsumption(updatedDevice);
      
      // Update in backend - using POST instead of PUT
      await axios.post(`${API_URL}/api/user/update-device-settings`, {
        user_id: userId,
        household_id: householdId,
        device_name: deviceToUpdate.name,
        settings: {
          temperature: temperature
        },
        calculated_power: calculatedPower // Send calculated power to backend
      });
      
      // Update in state
      setDevices(
        devices.map((device) => {
          if (device.id === id) {
            const updatedDevice = {
              ...device,
              temperature,
              powerConsumption: device.status === "on" ? 
                calculatedPower : 0,
              basePowerConsumption: device.basePowerConsumption // Preserve base power
            };
            return updatedDevice;
          }
          return device;
        })
      );
      
      // Update in localStorage
      localStorage.setItem(
        "devices",
        JSON.stringify(
          devices.map((device) => {
            if (device.id === id) {
              return {
                ...device,
                temperature,
                powerConsumption: device.status === "on" ? 
                  calculatedPower : 0,
                basePowerConsumption: device.basePowerConsumption // Preserve base power
              };
            }
            return device;
          })
        )
      );
    } catch (error) {
      console.error("Error updating temperature:", error);
                toast({
                    title: "Error",
        description: "Failed to update temperature. Please try again.",
                    variant: "destructive",
                });
            }
  };

  const updateFanSpeed = async (id: string, speed: number) => {
    try {
      const deviceToUpdate = devices.find((d) => d.id === id);
      if (!deviceToUpdate) return;
      
      // Get user info
      const storedUser = localStorage.getItem("currentUser");
      const storedMember = localStorage.getItem("currentMember");
      
      let userId: string | undefined = undefined;
      let householdId: string | undefined = undefined;
      
      if (storedUser) {
        const currentUser = JSON.parse(storedUser);
        userId = currentUser.id;
        householdId = currentUser.householdId;
      } else if (storedMember) {
        const currentMember = JSON.parse(storedMember);
        userId = currentMember.id;
        householdId = currentMember.householdId;
      }
      
      if (!userId) {
        console.error("No user ID found");
        return;
      }
      
      // Calculate new power consumption based on updated fan speed
      const updatedDevice = {...deviceToUpdate, speed};
      const calculatedPower = calculatePowerConsumption(updatedDevice);
      
      // Update in backend - using POST instead of PUT
      await axios.post(`${API_URL}/api/user/update-device-settings`, {
        user_id: userId,
        household_id: householdId,
        device_name: deviceToUpdate.name,
        settings: {
          speed: speed
        },
        calculated_power: calculatedPower // Send calculated power to backend
      });
      
      // Update in state
      setDevices(
        devices.map((device) => {
          if (device.id === id) {
            const updatedDevice = {
              ...device,
              speed,
              powerConsumption: device.status === "on" ? 
                calculatedPower : 0,
              basePowerConsumption: device.basePowerConsumption // Preserve base power
            };
            return updatedDevice;
          }
          return device;
        })
      );
      
      // Update in localStorage
      localStorage.setItem(
        "devices",
        JSON.stringify(
          devices.map((device) => {
            if (device.id === id) {
              return {
                ...device,
                speed,
                powerConsumption: device.status === "on" ? 
                  calculatedPower : 0,
                basePowerConsumption: device.basePowerConsumption // Preserve base power
              };
            }
            return device;
          })
        )
      );
    } catch (error) {
      console.error("Error updating fan speed:", error);
      toast({
        title: "Error",
        description: "Failed to update fan speed. Please try again.",
        variant: "destructive",
      });
    }
  };

    const saveEditedDevice = async () => {
    if (!editingDevice) return;
    
    try {
      // Get user info
      const storedUser = localStorage.getItem("currentUser");
      const storedMember = localStorage.getItem("currentMember");
      
      let userId: string | undefined = undefined;
      let householdId: string | undefined = undefined;
      
      if (storedUser) {
        const currentUser = JSON.parse(storedUser);
        userId = currentUser.id;
        householdId = currentUser.householdId;
      } else if (storedMember) {
        const currentMember = JSON.parse(storedMember);
        userId = currentMember.id;
        householdId = currentMember.householdId;
      }
      
      if (!userId) {
        console.error("No user ID found");
        toast({
          title: "Error",
          description: "User information not found. Please login again.",
          variant: "destructive",
        });
        return;
      }
      
      // Find the original device to get the old name
      const originalDevice = devices.find(d => d.id === editingDevice.id);
      if (!originalDevice) return;
      
      // Update in backend
      await axios.put(`${API_URL}/api/user/update-device`, {
                        user_id: userId,
        household_id: householdId,
                        old_device_name: originalDevice.name,
                        new_device_name: editingDevice.name,
                        room: editingDevice.room,
        base_power_consumption: editingDevice.basePowerConsumption
      });
      
      // Update in state
      setDevices(
        devices.map((device) => {
          if (device.id === editingDevice.id) {
            const updatedDevice = {
              ...editingDevice,
              powerConsumption: device.status === "on" ? 
                calculatePowerConsumption(editingDevice) : 0
            };
            return updatedDevice;
          }
          return device;
        })
      );
      
      // Update in localStorage
      localStorage.setItem(
        "devices",
        JSON.stringify(
          devices.map((device) => {
            if (device.id === editingDevice.id) {
              const updatedDevice = {
                ...editingDevice,
                powerConsumption: device.status === "on" ? 
                  calculatePowerConsumption(editingDevice) : 0
              };
              return updatedDevice;
            }
            return device;
          })
        )
      );
      
                setEditingDevice(null);
                
                toast({
                    title: "Device Updated",
        description: "Device settings have been updated successfully.",
                });
    } catch (error) {
      console.error("Error saving device:", error);
                toast({
                    title: "Error",
        description: "Failed to update device. Please try again.",
                    variant: "destructive",
                });
        }
    };

    const handleEditDevice = (device: Device) => {
        setEditingDevice(device)
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
                                onCheckedChange={(checked) => toggleDevice(device.id)}
                            />
                        </div>
                        {device.status === "on" && (
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span>Brightness</span>
                                    <span className="text-sm font-medium">{device.brightness || 100}%</span>
                                </div>
                                <Slider
                                    value={[device.brightness || 100]}
                                    onValueChange={([value]) => {
                                        // Add debug toast for brightness change
                                        toast({
                                            title: "Brightness changed",
                                            description: `${device.name} brightness set to ${value}%`,
                                        });
                                        updateBrightness(device.id, value);
                                    }}
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
                                onCheckedChange={(checked) => toggleDevice(device.id)}
                            />
                        </div>
                        {device.status === "on" && (
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span>Temperature (°C)</span>
                                    <span className="text-sm font-medium">{device.temperature || 22}°C</span>
                                </div>
                                <Slider
                                    value={[device.temperature || 22]}
                                    onValueChange={([value]) => {
                                        // Add debug toast for temperature change
                                        toast({
                                            title: "Temperature changed",
                                            description: `${device.name} temperature set to ${value}°C`,
                                        });
                                        updateTemperature(device.id, value);
                                    }}
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
                                onCheckedChange={(checked) => toggleDevice(device.id)}
                            />
                        </div>
                        {device.status === "on" && (
                            <div className="space-y-2">
                                <div className="flex justify-between">
                                    <span>Speed</span>
                                    <span className="text-sm font-medium">{device.speed || 1}</span>
                                </div>
                                <Slider
                                    value={[device.speed || 1]}
                                    onValueChange={([value]) => {
                                        // Add debug toast for fan speed change
                                        toast({
                                            title: "Fan speed changed",
                                            description: `${device.name} speed set to ${value}`,
                                        });
                                        updateFanSpeed(device.id, value);
                                    }}
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
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span>Power</span>
                            <Switch
                                checked={device.status === "on"}
                                onCheckedChange={(checked) => toggleDevice(device.id)}
                            />
                        </div>
                    </div>
                )
        }
    }

    const deleteDevice = async (id: string) => {
      try {
        const deviceToDelete = devices.find((d) => d.id === id);
        if (!deviceToDelete) return;
        
        // Get user info from localStorage
        const storedUser = localStorage.getItem("currentUser");
        const storedMember = localStorage.getItem("currentMember");
        
        let userId: string | undefined = undefined;
        let householdId: string | undefined = undefined;
        
        if (storedUser) {
          const currentUser = JSON.parse(storedUser);
          userId = currentUser.id;
          householdId = currentUser.householdId;
        } else if (storedMember) {
          const currentMember = JSON.parse(storedMember);
          userId = currentMember.id;
          householdId = currentMember.householdId;
        }
        
        if (!userId) {
          console.error("No user ID found");
          toast({
            title: "Error",
            description: "User information not found. Please login again.",
            variant: "destructive",
          });
          return;
        }
        
        // Delete from backend
        await axios.delete(`${API_URL}/api/user/delete-device`, {
          params: {
            user_id: userId,
            device_name: deviceToDelete.name,
            household_id: householdId
          }
        });
        
        // Remove from state
        setDevices(devices.filter((device) => device.id !== id));
        
        // Remove from localStorage
        localStorage.setItem(
          "devices",
          JSON.stringify(devices.filter((device) => device.id !== id))
        );
        
        toast({
          title: "Device Deleted",
          description: `${deviceToDelete.name} has been removed.`,
        });
      } catch (error) {
        console.error("Error deleting device:", error);
        toast({
          title: "Error",
          description: "Failed to delete device. Please try again.",
          variant: "destructive",
        });
      }
    };

    return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex">
            <NavigationSidebar />
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
        className="flex-1 ml-[72px] p-6"
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
                                                <div className="flex justify-between items-center p-2 bg-blue-50 rounded-md">
                                                    <span className="text-gray-700 text-sm">Power Consumption</span>
                                                    <span className={`font-medium ${device.status === "on" ? "text-blue-600" : "text-gray-600"}`}>
                                                        {device.status === "on" 
                                                            ? (device.powerConsumption?.toFixed(1) || "0.0") 
                                                            : (calculatePowerConsumption({...device, status: "on"}).toFixed(1))} W
                                                    </span>
                                                </div>
                                                <div className="flex items-center justify-between text-sm">
                                                    <span className="text-gray-500">Total Energy Consumed</span>
                                                    <span className="font-medium">{(device.totalEnergyConsumed || 0).toFixed(2)} kWh</span>
                                                </div>
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
            <Dialog open={editingDevice !== null} onOpenChange={() => setEditingDevice(null)}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Edit Device</DialogTitle>
                    </DialogHeader>
                    {editingDevice && (
                        <div className="grid gap-4 py-4">
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="name" className="text-right">
                                    Name
                                </Label>
                                <Input
                                    id="name"
                                    value={editingDevice.name}
                                    onChange={(e) => setEditingDevice({ ...editingDevice, name: e.target.value })}
                                    className="col-span-3"
                                />
                            </div>
                            <div className="grid grid-cols-4 items-center gap-4">
                                <Label htmlFor="room" className="text-right">
                                    Room
                                </Label>
                                <Input
                                    id="room"
                                    value={editingDevice.room}
                                    onChange={(e) => setEditingDevice({ ...editingDevice, room: e.target.value })}
                                    className="col-span-3"
                                />
                            </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="basePower" className="text-right">
                    Base Power (W)
                  </Label>
                  <Input
                    id="basePower"
                    type="number"
                    value={editingDevice.basePowerConsumption || BASE_POWER_CONSUMPTION[editingDevice.type] || 10}
                    onChange={(e) =>
                      setEditingDevice({
                        ...editingDevice,
                        basePowerConsumption: Number(e.target.value),
                      })
                    }
                                    className="col-span-3"
                                />
                            </div>
                        </div>
                    )}
                    <DialogFooter>
                        <Button onClick={saveEditedDevice}>Save changes</Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
      </motion.div>
        </div>
    )
}

