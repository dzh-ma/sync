// components/active-devices.tsx
import { useState, useEffect } from "react";
import { Light, Thermometer, Lock, Camera, Smartphone } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Toggle } from "@/components/ui/toggle";

// Define types to match the backend models
interface Device {
  id: string;
  name: string;
  type: string;
  status: string;
  last_online: string;
  room_id: string;
  settings: any;
}

interface Room {
  id: string;
  name: string;
}

interface ActiveDevicesProps {
  userId: string;
  createAuthHeaders: () => Record<string, string>;
  apiUrl: string;
  isDarkMode?: boolean;
}

export function ActiveDevices({ userId, createAuthHeaders, apiUrl, isDarkMode = false }: ActiveDevicesProps) {
  const [devices, setDevices] = useState<Device[]>([]);
  const [rooms, setRooms] = useState<Record<string, Room>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch devices from the backend
  useEffect(() => {
    const fetchDevices = async () => {
      if (!userId) return;

      try {
        setLoading(true);
        const response = await fetch(`${apiUrl}/devices?user_id=${userId}&status=online`, {
          headers: createAuthHeaders()
        });

        if (!response.ok) {
          throw new Error(`Error fetching devices: ${response.statusText}`);
        }

        const devicesData = await response.json();
        setDevices(devicesData.slice(0, 5)); // Show only the first 5 devices

        // Fetch rooms to map room_id to room names
        const roomsResponse = await fetch(`${apiUrl}/rooms?user_id=${userId}`, {
          headers: createAuthHeaders()
        });

        if (roomsResponse.ok) {
          const roomsData = await roomsResponse.json();
          const roomsMap = roomsData.reduce((acc: Record<string, Room>, room: Room) => {
            acc[room.id] = room;
            return acc;
          }, {});
          setRooms(roomsMap);
        }
      } catch (error) {
        console.error("Error fetching devices:", error);
        setError("Failed to load devices. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchDevices();
  }, [userId, apiUrl, createAuthHeaders]);

  // Toggle device on/off
  const toggleDevice = async (deviceId: string, isOn: boolean) => {
    try {
      const deviceToUpdate = devices.find(d => d.id === deviceId);
      if (!deviceToUpdate) return;

      // Create a copy of the settings with the updated state
      const newSettings = {
        ...deviceToUpdate.settings,
        on: !isOn
      };

      // Update the device in the backend
      const response = await fetch(`${apiUrl}/devices/${deviceId}`, {
        method: 'PATCH',
        headers: createAuthHeaders(),
        body: JSON.stringify({
          settings: newSettings
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to update device: ${response.statusText}`);
      }

      // Update local state
      setDevices(devices.map(device => 
        device.id === deviceId 
          ? {...device, settings: newSettings} 
          : device
      ));
    } catch (error) {
      console.error("Error toggling device:", error);
    }
  };

  // Get device icon based on type
  const getDeviceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'light':
        return <Light className="h-5 w-5" />;
      case 'thermostat':
        return <Thermometer className="h-5 w-5" />;
      case 'lock':
        return <Lock className="h-5 w-5" />;
      case 'camera':
        return <Camera className="h-5 w-5" />;
      default:
        return <Smartphone className="h-5 w-5" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-2">
        <h3 className="text-sm font-medium">Active Devices</h3>
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 bg-gray-200 rounded-md"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-2">
        <h3 className="text-sm font-medium">Active Devices</h3>
        <div className={`p-4 rounded-md ${isDarkMode ? 'bg-red-900/20' : 'bg-red-50'} text-red-500`}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium">Active Devices</h3>
      <div className="space-y-3">
        {devices.length === 0 ? (
          <div className={`p-4 rounded-md ${isDarkMode ? 'bg-gray-800' : 'bg-gray-100'} text-center`}>
            No active devices found
          </div>
        ) : (
          devices.map((device) => {
            // Get is device on/off from settings
            const isOn = device.settings?.on === true;
            // Get brightness percentage if available
            const brightness = device.settings?.brightness || 0;
            const roomName = device.room_id && rooms[device.room_id] ? rooms[device.room_id].name : "Unknown Room";

            return (
              <div
                key={device.id}
                className={`p-2 rounded-lg flex items-center justify-between ${
                  isDarkMode ? 'bg-gray-800' : 'bg-gray-100'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-full ${isOn ? 'bg-blue-100 text-blue-600' : 'bg-gray-200 text-gray-500'}`}>
                    {getDeviceIcon(device.type)}
                  </div>
                  <div>
                    <h4 className="text-sm font-medium">{device.name}</h4>
                    <p className="text-xs text-gray-500">{roomName}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {device.type === 'light' && (
                    <div className="w-16">
                      <Progress value={brightness} max={100} className="h-1" />
                    </div>
                  )}
                  <Toggle
                    aria-label={`Toggle ${device.name}`}
                    pressed={isOn}
                    onPressedChange={() => toggleDevice(device.id, isOn)}
                    size="sm"
                    variant={isOn ? "default" : "outline"}
                  />
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
