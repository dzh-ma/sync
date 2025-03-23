"use client"

import { NavigationSidebar } from "../components/navigation-sidebar"
import { Button } from "@/components/ui/button"
import { Plus, User, Home } from "lucide-react"
import { useState, useEffect } from "react"
import { RoomCard } from "./room-card"
import { AddRoomDialog } from "./add-room-dialog"
import { Card } from "@/components/ui/card"
import Link from "next/link"
import { toast } from "@/components/ui/use-toast"

interface Room {
  id: string;
  name: string;
  type: string;
  image: string;
}

export default function RoomsPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    setIsLoading(true);
    try {
      // Get user info from localStorage
      const storedUser = localStorage.getItem("currentUser");
      const storedMember = localStorage.getItem("currentMember");
      
      let userId, householdId;
      
      if (storedUser) {
        const currentUser = JSON.parse(storedUser);
        userId = currentUser.id;
        householdId = currentUser.householdId;
      } else if (storedMember) {
        const currentMember = JSON.parse(storedMember);
        userId = currentMember.id;
        householdId = currentMember.householdId;
      }
      
      // Check for missing householdId
      if (!householdId) {
        // Check if we have a generated one
        const generatedHouseholdId = localStorage.getItem("generatedHouseholdId");
        
        if (generatedHouseholdId) {
          householdId = generatedHouseholdId;
          
          // Update the user object with this generated householdId
          if (storedUser) {
            const currentUser = JSON.parse(storedUser);
            currentUser.householdId = householdId;
            localStorage.setItem("currentUser", JSON.stringify(currentUser));
          } else if (storedMember) {
            const currentMember = JSON.parse(storedMember);
            currentMember.householdId = householdId;
            localStorage.setItem("currentMember", JSON.stringify(currentMember));
          }
        } else {
          // Generate a new householdId
          householdId = `default-household-${Date.now()}`;
          localStorage.setItem("generatedHouseholdId", householdId);
          
          // Update the user object
          if (storedUser) {
            const currentUser = JSON.parse(storedUser);
            currentUser.householdId = householdId;
            localStorage.setItem("currentUser", JSON.stringify(currentUser));
          } else if (storedMember) {
            const currentMember = JSON.parse(storedMember);
            currentMember.householdId = householdId;
            localStorage.setItem("currentMember", JSON.stringify(currentMember));
          }
        }
      }

      const response = await fetch(`http://localhost:8000/api/rooms?household_id=${householdId}`);
      
      if (!response.ok) {
        if (response.status === 422) {
          throw new Error("Household ID not found. Please login again.");
        }
        throw new Error(`Error fetching rooms: ${response.statusText}`);
      }
      
      const data = await response.json();
      setRooms(data);
      
      // Update local storage with rooms
      localStorage.setItem("rooms", JSON.stringify(data));
    } catch (error: any) {
      console.error("Failed to fetch rooms:", error);
      
      // Check if it's the specific household ID error
      if (error instanceof Error && error.message.includes("Household ID not found")) {
        setError("Household ID not found. Please login again.");
        toast({
          title: "Error",
          description: "Household ID not found. Please login again.",
          variant: "destructive",
        });
      } else {
        setError("Failed to load rooms. Please try again.");
        toast({
          title: "Error",
          description: "Failed to load rooms. Please try again.",
          variant: "destructive",
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddRoom = async (newRoom: { name: string; type: string; image: string }) => {
    try {
      const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
      const householdId = currentUser.householdId;
      
      if (!householdId) {
        throw new Error("Household ID not found. Please login again.");
      }
      
      const response = await fetch("http://localhost:8000/api/rooms/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...newRoom,
          household_id: householdId,
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || "Failed to add room");
      }
      
      const data = await response.json();
      
      // Add the new room to the state
      setRooms([...rooms, data.room]);
      setIsDialogOpen(false);
      
      toast({
        title: "Success",
        description: "Room added successfully!",
      });
    } catch (error: any) {
      console.error("Error adding room:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to add room",
        variant: "destructive",
      });
    }
  };

  const handleDeleteRoom = async (id: string) => {
    try {
      const roomToDelete = rooms.find(room => room.id === id);
      if (!roomToDelete) {
        throw new Error("Room not found");
      }

      const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
      const householdId = currentUser.householdId;
      const userId = currentUser.id;
      
      if (!householdId) {
        throw new Error("Household ID not found. Please login again.");
      }
      
      // 1. Delete the room from the backend
      const response = await fetch(`http://localhost:8000/api/rooms/delete?room_id=${id}&household_id=${householdId}`, {
        method: "DELETE",
      });
      
      if (!response.ok) {
        throw new Error("Failed to delete room");
      }
      
      // 2. Find all devices associated with this room
      const allDevices = JSON.parse(localStorage.getItem("devices") || "[]");
      const devicesInRoom = allDevices.filter((device: any) => device.room === roomToDelete.name);
      
      console.log(`Found ${devicesInRoom.length} devices in room "${roomToDelete.name}"`);
      
      // 3. Delete each device associated with this room
      for (const device of devicesInRoom) {
        try {
          console.log(`Deleting device "${device.name}" from room "${roomToDelete.name}"`);
          
          // Delete from backend
          await fetch(`http://localhost:8000/api/user/delete-device?user_id=${userId}&device_name=${encodeURIComponent(device.name)}&household_id=${householdId}`, {
            method: "DELETE"
          });
          
        } catch (deviceError) {
          console.error(`Error deleting device "${device.name}":`, deviceError);
          // Continue with other devices even if one fails
        }
      }
      
      // 4. Update devices in localStorage - remove all devices in this room
      const updatedDevices = allDevices.filter((device: any) => device.room !== roomToDelete.name);
      localStorage.setItem("devices", JSON.stringify(updatedDevices));
      
      // 5. Update the rooms state
      const updatedRooms = rooms.filter((room) => room.id !== id);
      setRooms(updatedRooms);
      
      // 6. Update rooms in localStorage
      localStorage.setItem("rooms", JSON.stringify(updatedRooms));
      
      toast({
        title: "Success",
        description: `Room deleted successfully${devicesInRoom.length > 0 ? ` along with ${devicesInRoom.length} device${devicesInRoom.length === 1 ? '' : 's'}` : ''}!`,
      });
    } catch (error: any) {
      console.error("Error deleting room:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to delete room",
        variant: "destructive",
      });
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <NavigationSidebar />
        <div className="flex-1 ml-[72px] p-6 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#00B2FF] mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading rooms...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavigationSidebar />
      <div className="ml-[72px] p-6">
        <header className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-[#00B2FF] rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-xl">Sy</span>
            </div>
            <h1 className="text-2xl font-bold">Room List</h1>
          </div>
          <Button variant="ghost" size="icon">
            <User className="h-5 w-5" />
          </Button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {rooms.length === 0 ? (
            <Card className="col-span-full p-6 text-center">
              <div className="flex flex-col items-center justify-center space-y-4">
                <div className="rounded-full bg-blue-100 p-3">
                  <Home className="h-8 w-8 text-[#00B2FF]" />
                </div>
                <div className="space-y-2">
                  <h3 className="font-semibold text-lg">No rooms added yet</h3>
                  <p className="text-muted-foreground">Start by adding your first room to manage your smart home</p>
                </div>
                <Link href="/add-room">
                  <Button className="bg-[#00B2FF] hover:bg-[#00B2FF]/90">
                    <Plus className="mr-2 h-4 w-4" /> Add Your First Room
                  </Button>
                </Link>
              </div>
            </Card>
          ) : (
            <>
              {rooms.map((room) => (
                <RoomCard 
                  key={room.id} 
                  id={room.id}
                  name={room.name} 
                  type={room.type}
                  image={room.image || "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/IMG_0697-MRkZkq9qJMNVm20BYSDpYOdkYHt3pF.jpeg"} 
                  onDelete={handleDeleteRoom}
                />
              ))}
              <button
                onClick={() => setIsDialogOpen(true)}
                className="aspect-video bg-white rounded-lg border-2 border-dashed border-gray-200 flex flex-col items-center justify-center gap-2 hover:border-[#00B2FF] transition-colors"
              >
                <Plus className="h-8 w-8 text-[#00B2FF]" />
                <span className="text-[#00B2FF] font-medium">Add a Room</span>
              </button>
            </>
          )}
        </div>

        <AddRoomDialog open={isDialogOpen} onOpenChange={setIsDialogOpen} onAdd={handleAddRoom} />
      </div>
    </div>
  )
}

