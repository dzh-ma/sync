// dashboard/page.tsx
"use client";

import { useState, useEffect } from "react";
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import { arrayMove, SortableContext, sortableKeyboardCoordinates, rectSortingStrategy } from "@dnd-kit/sortable";
import { Edit2, Download, Bell, Command, HelpCircle, Sun, Moon, Lock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ActiveDevices } from "../components/active-devices";
import { EnergyConsumption } from "../components/energy-consumption";
import { FamilyMembers } from "../components/family-members";
import { WeatherWidget } from "../components/weather-widget";
import { SortableWidget } from "../components/sortable-widget";
import { AutomationWidget } from "../components/automation-widget";
import { RoomEnergyConsumption } from "../components/room-energy-consumption";
import { TimeDateWidget } from "../components/time-date-widget";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { toast } from "@/components/ui/use-toast";
import { useUser } from "@/contexts/UserContext"; // Import the user context
import { NavigationSidebar } from "@/app/components/navigation-sidebar"; 
import ProtectedRoute from "@/components/ProtectedRoute"; // Import the protected route component

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const initialWidgets = [
  { id: "time-date", component: TimeDateWidget },
  { id: "devices", component: ActiveDevices },
  { id: "weather", component: WeatherWidget },
  { id: "energy", component: EnergyConsumption },
  { id: "automation", component: AutomationWidget },
]

export default function Page() {
  const router = useRouter();
  const { user } = useUser(); // Use the user context
  
  const [rooms, setRooms] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [widgets, setWidgets] = useState(initialWidgets);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [userPermissions, setUserPermissions] = useState({
    statisticalData: true,
    addAutomation: true,
    roomControl: true
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to create headers with HTTP Basic Authentication
  const createAuthHeaders = () => {
    if (!user || !user.username || !user.password) {
      return {};
    }
    const credentials = btoa(`${user.username}:${user.password}`);
    return {
      'Authorization': `Basic ${credentials}`,
      'Content-Type': 'application/json'
    };
  };

  // Fetch user's rooms from the backend
  useEffect(() => {
    const fetchRooms = async () => {
      if (!user) return;

      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/rooms`, {
          headers: createAuthHeaders()
        });
        
        if (!response.ok) {
          throw new Error(`Error fetching rooms: ${response.statusText}`);
        }
        
        const roomsData = await response.json();
        
        // Fetch usage data for each room to get energy consumption
        const roomsWithConsumption = await Promise.all(roomsData.map(async (room) => {
          try {
            // Get devices in this room
            const devicesResponse = await fetch(`${API_URL}/devices?room_id=${room.id}`, {
              headers: createAuthHeaders()
            });
            
            if (!devicesResponse.ok) {
              return { ...room, consumption: 0 };
            }
            
            const devices = await devicesResponse.json();
            let totalConsumption = 0;
            
            // For each device, get its energy consumption
            for (const device of devices) {
              const usageResponse = await fetch(`${API_URL}/usage?device_id=${device.id}&limit=30`, {
                headers: createAuthHeaders()
              });
              
              if (usageResponse.ok) {
                const usageData = await usageResponse.json();
                totalConsumption += usageData.reduce((sum, record) => 
                  sum + (record.energy_consumed || 0), 0);
              }
            }
            
            return {
              ...room,
              consumption: parseFloat(totalConsumption.toFixed(2))
            };
          } catch (error) {
            console.error(`Error fetching consumption for room ${room.id}:`, error);
            return { ...room, consumption: 0 };
          }
        }));
        
        setRooms(roomsWithConsumption);
      } catch (error) {
        console.error("Error fetching rooms:", error);
        setError(error.message);
        // If API fails, use fallback data
        setRooms([
          { id: "1", name: "Living Room", consumption: 45 },
          { id: "2", name: "Bedroom", consumption: 18 },
          { id: "3", name: "Kitchen", consumption: 72 },
          { id: "4", name: "Bathroom", consumption: 12 },
          { id: "5", name: "Office", consumption: 35 },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchRooms();
  }, [user]);

  // Check user's access to features based on role
  useEffect(() => {
    const checkUserPermissions = async () => {
      if (!user) return;

      try {
        // Get user profile
        const response = await fetch(`${API_URL}/users/${user.id}`, {
          headers: createAuthHeaders()
        });
        
        if (!response.ok) {
          throw new Error(`Error fetching user profile: ${response.statusText}`);
        }
        
        const userData = await response.json();
        
        // Set permissions based on user role
        const isAdmin = userData.role === 'admin';
        setUserPermissions({
          statisticalData: true, // Everyone can see stats
          addAutomation: isAdmin, // Only admins can add automations
          roomControl: true // Everyone can control rooms
        });
        
        // Filter widgets based on permissions
        const filteredWidgets = initialWidgets.filter((widget) => {
          if (widget.id === "energy" && !userPermissions.statisticalData) return false;
          if (widget.id === "automation" && !userPermissions.addAutomation) return false;
          return true;
        });
        
        setWidgets(filteredWidgets);
      } catch (error) {
        console.error("Error checking user permissions:", error);
        // Fallback to default permissions on error
      }
    };

    checkUserPermissions();
  }, [user]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  function handleDragEnd(event) {
    const { active, over } = event;

    if (active.id !== over.id) {
      setWidgets((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id);
        const newIndex = items.findIndex((item) => item.id === over.id);
        return arrayMove(items, oldIndex, newIndex);
      });
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
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
    },
  };

  const handleRequestAccess = (feature) => {
    // Create a notification requesting access
    const createNotification = async () => {
      try {
        const response = await fetch(`${API_URL}/notifications`, {
          method: 'POST',
          headers: createAuthHeaders(),
          body: JSON.stringify({
            user_id: user.id,
            title: `Access Request: ${feature}`,
            message: `User ${user.username} is requesting access to ${feature}.`,
            type: "info",
            priority: "medium",
            source: "system",
            read: false
          })
        });
        
        if (!response.ok) {
          throw new Error(`Failed to send request: ${response.statusText}`);
        }
        
        toast({
          title: "Access Requested",
          description: `Your request for access to ${feature} has been sent to the admin.`,
        });
      } catch (error) {
        console.error("Error requesting access:", error);
        toast({
          title: "Request Failed",
          description: "There was an error sending your access request. Please try again.",
          variant: "destructive"
        });
      }
    };
    
    createNotification();
  };

  // Function to generate an energy report
  const handleGenerateReport = async () => {
    try {
      const response = await fetch(`${API_URL}/reports`, {
        method: 'POST',
        headers: createAuthHeaders(),
        body: JSON.stringify({
          user_id: user.id,
          format: "pdf",
          report_type: "energy",
          title: "Energy Usage Report"
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to generate report: ${response.statusText}`);
      }
      
      const reportData = await response.json();
      
      toast({
        title: "Report Generated",
        description: "Your energy report is being generated. You'll be notified when it's ready to download.",
      });
      
      // Poll for report completion
      const checkReportStatus = async () => {
        const statusResponse = await fetch(`${API_URL}/reports/${reportData.id}`, {
          headers: createAuthHeaders()
        });
        
        if (statusResponse.ok) {
          const status = await statusResponse.json();
          
          if (status.status === "completed" && status.download_url) {
            toast({
              title: "Report Ready",
              description: "Your energy report is ready. Click here to download.",
              action: (
                <Button variant="outline" onClick={() => window.open(`${API_URL}${status.download_url}`, '_blank')}>
                  Download
                </Button>
              )
            });
            return true;
          } else if (status.status === "failed") {
            toast({
              title: "Report Failed",
              description: "There was an error generating your report. Please try again.",
              variant: "destructive"
            });
            return true;
          }
        }
        
        return false;
      };
      
      // Check status every 3 seconds for up to 30 seconds
      let attempts = 0;
      const maxAttempts = 10;
      
      const intervalId = setInterval(async () => {
        attempts++;
        const isDone = await checkReportStatus();
        
        if (isDone || attempts >= maxAttempts) {
          clearInterval(intervalId);
        }
      }, 3000);
      
    } catch (error) {
      console.error("Error generating report:", error);
      toast({
        title: "Report Generation Failed",
        description: "There was an error generating your report. Please try again.",
        variant: "destructive"
      });
    }
  };

  // Wrap the entire dashboard in the ProtectedRoute component
  return (
    <ProtectedRoute>
      <div className={`p-6 min-h-screen ${isDarkMode ? "bg-gray-900 text-white" : "bg-gray-50 text-gray-900"}`}>
        <NavigationSidebar />
        <div className="ml-[72px]">
          <motion.header variants={itemVariants} className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">Sy</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold">Welcome Home, {user?.username || "User"}</h1>
                <p className="text-sm text-gray-500">Your smart home dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {userPermissions.addAutomation && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsEditing(!isEditing)}
                  className={isEditing ? "bg-blue-100" : ""}
                >
                  <Edit2 className="h-5 w-5" />
                </Button>
              )}
              <Button variant="ghost" size="icon" onClick={handleGenerateReport}>
                <Download className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon">
                <Bell className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon">
                <Command className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon">
                <HelpCircle className="h-5 w-5" />
              </Button>
              <Button variant="ghost" size="icon" onClick={() => setIsDarkMode(!isDarkMode)}>
                {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </Button>
            </div>
          </motion.header>

          <div className="grid grid-cols-12 gap-6">
            <motion.div variants={itemVariants} className="col-span-12 lg:col-span-8">
              {userPermissions.roomControl ? (
                <Card className={`mb-6 ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
                  <CardHeader>
                    <CardTitle>Room Energy Overview</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {loading ? (
                      <div className="flex justify-center items-center h-40">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                      </div>
                    ) : error ? (
                      <div className="text-center text-red-500">
                        <p>Error loading room data.</p>
                        <Button variant="outline" onClick={() => window.location.reload()} className="mt-2">
                          Retry
                        </Button>
                      </div>
                    ) : (
                      <RoomEnergyConsumption rooms={rooms} />
                    )}
                  </CardContent>
                </Card>
              ) : (
                <Card className={`mb-6 ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
                  <CardContent className="flex flex-col items-center justify-center p-6">
                    <Lock className="w-12 h-12 text-gray-400 mb-4" />
                    <h3 className="text-lg font-semibold mb-2">Access Required</h3>
                    <p className="text-sm text-gray-500 text-center mb-4">
                      You don't have permission to view room control data.
                    </p>
                    <Button onClick={() => handleRequestAccess("Room Control")}>Request Access</Button>
                  </CardContent>
                </Card>
              )}
              <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  <SortableContext items={widgets.map((w) => w.id)} strategy={rectSortingStrategy}>
                    {widgets.map((widget) => (
                      <SortableWidget key={widget.id} id={widget.id} isEditing={isEditing}>
                        <Card className={`h-full ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
                          <CardContent className="p-4">
                            <widget.component 
                              userId={user?.id} 
                              username={user?.username}
                              createAuthHeaders={createAuthHeaders}
                              apiUrl={API_URL}
                              isDarkMode={isDarkMode}
                            />
                          </CardContent>
                        </Card>
                      </SortableWidget>
                    ))}
                  </SortableContext>
                </div>
              </DndContext>
            </motion.div>
            <motion.div variants={itemVariants} className="col-span-12 lg:col-span-4">
              <Card className={`h-full ${isDarkMode ? "bg-gray-800" : "bg-white"}`}>
                <CardHeader>
                  <CardTitle>Family Members</CardTitle>
                </CardHeader>
                <CardContent>
                  <FamilyMembers 
                    userId={user?.id}
                    createAuthHeaders={createAuthHeaders}
                    apiUrl={API_URL}
                    isDarkMode={isDarkMode}
                  />
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
