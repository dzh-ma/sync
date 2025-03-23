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
import { useUser } from "@/contexts/UserContext"; 
import { NavigationSidebar } from "@/app/components/navigation-sidebar"; 
import ProtectedRoute from "@/components/ProtectedRoute";
import { deviceApi, roomApi, energyApi } from "@/lib/api";

const initialWidgets = [
  { id: "time-date", component: TimeDateWidget },
  { id: "devices", component: ActiveDevices },
  { id: "weather", component: WeatherWidget },
  { id: "energy", component: EnergyConsumption },
  { id: "automation", component: AutomationWidget },
];

export default function Page() {
  const router = useRouter();
  const { user } = useUser();
  
  const [rooms, setRooms] = useState([]);
  const [isEditing, setIsEditing] = useState(false);
  const [widgets, setWidgets] = useState(initialWidgets);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [userPermissions, setUserPermissions] = useState({
    statisticalData: true,
    addAutomation: true,
    roomControl: true
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setIsLoading(true);
      try {
        // Fetch rooms data
        const roomsData = await roomApi.getRooms();
        setRooms(roomsData);
        
        // In a production app, you would fetch permissions from your backend
        // For now we'll simulate this based on the user's email
        if (user) {
          const mockPermissions = {
            statisticalData: true,
            addAutomation: user.email?.includes("admin") ? true : false,
            roomControl: true
          };
          
          setUserPermissions(mockPermissions);
          
          // Filter widgets based on permissions
          const filteredWidgets = initialWidgets.filter((widget) => {
            if (widget.id === "energy" && !mockPermissions.statisticalData) return false;
            if (widget.id === "automation" && !mockPermissions.addAutomation) return false;
            return true;
          });
          
          setWidgets(filteredWidgets);
        }
      } catch (err) {
        console.error("Error fetching dashboard data:", err);
        setError(err.message || "Failed to fetch dashboard data");
        toast({
          title: "Error",
          description: "Failed to load dashboard data. Please try again.",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchDashboardData();
    }
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
    toast({
      title: "Access Requested",
      description: `Your request for access to ${feature} has been sent to the admin.`,
    });
  };

  // Wrap the entire dashboard in the ProtectedRoute component
  return (
    <ProtectedRoute>
      <div className={`p-6 min-h-screen ${isDarkMode ? "bg-gray-900 text-white" : "bg-gray-50 text-gray-900"}`}>
        <NavigationSidebar />
        <div className="ml-[72px]">
          {isLoading ? (
            <div className="flex items-center justify-center h-screen">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#00B2FF]"></div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-screen">
              <Card className="w-full max-w-md">
                <CardContent className="flex flex-col items-center justify-center p-6">
                  <HelpCircle className="w-12 h-12 text-red-500 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Error Loading Dashboard</h3>
                  <p className="text-sm text-gray-500 text-center mb-4">
                    {error}
                  </p>
                  <Button onClick={() => window.location.reload()}>Try Again</Button>
                </CardContent>
              </Card>
            </div>
          ) : (
            <>
              <motion.header variants={itemVariants} className="flex justify-between items-center mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                    <span className="text-white font-bold text-xl">Sy</span>
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold">Welcome Home, {user?.email?.split("@")[0] || "User"}</h1>
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
                  <Button variant="ghost" size="icon">
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
                        <RoomEnergyConsumption rooms={rooms} />
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
                                  email={user?.email}
                                  token={user?.token}
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
                      <FamilyMembers userId={user?.id} />
                    </CardContent>
                  </Card>
                </motion.div>
              </div>
            </>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
