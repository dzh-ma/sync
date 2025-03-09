import React from "react";
import { useState, useEffect } from "react";
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors } from "@dnd-kit/core";
import { arrayMove, SortableContext, sortableKeyboardCoordinates, rectSortingStrategy } from "@dnd-kit/sortable";
import { Edit2, Download, Bell, Command, HelpCircle, Sun, Moon, Lock } from "lucide-react";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { ActiveDevices } from "../components/active-devices";
import { EnergyConsumption } from "../components/energy-consumption";
import { FamilyMembers } from "../components/family-members";
import { WeatherWidget } from "../components/weather-widget";
import { SortableWidget } from "../components/sortable-widget";
import { AutomationWidget } from "../components/automation-widget";
import { RoomEnergyConsumption } from "../components/room-energy-consumption";
import { TimeDateWidget } from "../components/time-date-widget";
import { motion } from "framer-motion";
// Replace Next.js router with browser navigation
import { useNavigate } from "react-router-dom";
import { toast } from "../../components/ui/use-toast";
import axios from "axios";
import { NavigationSidebar } from "../../components/navigation-sidebar"; // Import the navbar

// Fix 1: Add TypeScript interface for widget props
interface WidgetProps {
  userId: string;
  householdId: string;
}

// Fix 2: Fix the import.meta.env type
const API_URL = (import.meta as any).env.VITE_API_URL || 'http://localhost:8000';

// Fix 3: Update the initialWidgets type
const initialWidgets = [
  { id: "time-date", component: TimeDateWidget as React.ComponentType<WidgetProps> },
  { id: "devices", component: ActiveDevices as React.ComponentType<WidgetProps> },
  { id: "weather", component: WeatherWidget as React.ComponentType<WidgetProps> },
  { id: "energy", component: EnergyConsumption as React.ComponentType<WidgetProps> },
  { id: "automation", component: AutomationWidget as React.ComponentType<WidgetProps> },
];

export default function Page() {
  const navigate = useNavigate();
  const [rooms, setRooms] = useState([
    { id: "1", name: "Living Room", consumption: 45 },
    { id: "2", name: "Bedroom", consumption: 18 },
    { id: "3", name: "Kitchen", consumption: 72 },
    { id: "4", name: "Bathroom", consumption: 12 },
    { id: "5", name: "Office", consumption: 35 },
  ])
  const [isEditing, setIsEditing] = useState(false)
  const [widgets, setWidgets] = useState(initialWidgets)
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    const storedUser = localStorage.getItem("currentUser");
    if (!storedUser) {
      navigate("/auth/login");
      return;
    }

    const currentUser = JSON.parse(storedUser);

    const fetchUserData = async () => {
      try {
        const userResponse = await axios.get(`${API_URL}/api/user/${currentUser.id}`);
        const userData = userResponse.data;

        const permissionsResponse = await axios.get(`${API_URL}/api/permissions/${userData.admin_email}`);
        const permissionsData = permissionsResponse.data;

        const updatedUser = { ...userData, ...currentUser, permissions: permissionsData };
        setUser(updatedUser);
        localStorage.setItem("currentUser", JSON.stringify(updatedUser));

      } catch (error) {
        console.error("Error fetching user data or permissions:", error);
        toast({
          title: "Error",
          description: "Failed to load user data. Please try again.",
          variant: "destructive",
        });
        navigate("/auth/login");
      }
    };

    fetchUserData();
  }, [navigate]);

  useEffect(() => {
    if (user) {
      const filteredWidgets = initialWidgets.filter((widget) => {
        if (widget.id === "energy" && !user.permissions?.statisticalData) return false;
        if (widget.id === "automation" && !user.permissions?.addAutomation) return false;
        return true;
      });
      setWidgets(filteredWidgets);
    }
  }, [user]);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  )

  function handleDragEnd(event: any) {
    const { active, over } = event

    if (active.id !== over.id) {
      setWidgets((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id)
        const newIndex = items.findIndex((item) => item.id === over.id)
        return arrayMove(items, oldIndex, newIndex)
      })
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

  const handleRequestAccess = (feature: string) => {
    // In a real application, this would send a request to the admin
    toast({
      title: "Access Requested",
      description: `Your request for access to ${feature} has been sent to the admin.`,
    })
  }

  if (!user) return null

  return (
    <div className={`p-6 min-h-screen bg-gray-50 ${isDarkMode ? "bg-gray-900 text-white" : "bg-gray-50 text-gray-900"}`}>
      <NavigationSidebar /> {/* Add the navbar here */}
      <div className="ml-[72px]">
        <motion.header variants={itemVariants} className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">Sy</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold">Welcome Home, {user.firstName}</h1>
              <p className="text-sm text-gray-500">Your smart home dashboard</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {user.type === "admin" && user.permissions?.addAutomation && (
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
            {user.permissions?.roomControl ? (
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
                          {/* Fix 4: Component rendering with proper typing */}
                          {React.createElement(widget.component, {
                            userId: user.id,
                            householdId: user.household_id
                          })}
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
                <FamilyMembers />
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
