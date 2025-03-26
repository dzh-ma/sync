"use client";

import type React from "react";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { User, Upload, Trash2, ArrowLeft, Home } from "lucide-react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { motion } from "framer-motion";
import { NavigationSidebar } from "@/app/components/navigation-sidebar";
import { toast } from "@/components/ui/use-toast";

interface Room {
  id: string;
  name: string;
  type: string;
  image: string;
}

export default function AddRoomPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    name: "",
    type: "",
    image: "",
  });
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      // Get user info from localStorage
      const storedUser = localStorage.getItem("currentUser");
      const storedMember = localStorage.getItem("currentMember");
      
      let householdId;
      
      if (storedUser) {
        const currentUser = JSON.parse(storedUser);
        householdId = currentUser.householdId;
      } else if (storedMember) {
        const currentMember = JSON.parse(storedMember);
        householdId = currentMember.householdId;
      }

      // If no householdId found, check for a generated one or create a new one
      if (!householdId) {
        console.warn("Missing householdId for fetching rooms. Checking for generated ID.");
        
        // Check if we have a generated householdId in localStorage
        const generatedHouseholdId = localStorage.getItem("generatedHouseholdId");
        
        if (generatedHouseholdId) {
          console.log("Using previously generated householdId for fetching rooms:", generatedHouseholdId);
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
          // Generate a new household ID
          householdId = `household-${Date.now()}`;
          console.log("Generated new householdId for fetching rooms:", householdId);
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
        throw new Error("Failed to fetch rooms");
      }

      const data = await response.json();
      setRooms(data);
    } catch (error) {
      console.error("Error fetching rooms:", error);
      toast({
        title: "Error",
        description: "Failed to load rooms",
        variant: "destructive",
      });
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData({ ...formData, image: reader.result as string });
        // Show toast notification when image is successfully selected
        toast({
          title: "Image Selected",
          description: `${file.name} has been successfully added`,
          duration: 3000, // Show for 5 seconds
        });
      };
      reader.readAsDataURL(file);
    } else {
      setFormData({ ...formData, image: "/minimal2.png" });
      toast({
        title: "Default Image",
        description: "No image selected, using default image",
        duration: 5000, // Show for 5 seconds
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
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

      // If no householdId found, check for a generated one or create a new one
      if (!householdId) {
        console.warn("Missing householdId. Checking for generated ID or creating a new one.");
        
        // Check if we have a generated householdId in localStorage
        const generatedHouseholdId = localStorage.getItem("generatedHouseholdId");
        
        if (generatedHouseholdId) {
          console.log("Using previously generated householdId:", generatedHouseholdId);
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
          // Generate a new household ID
          householdId = `household-${Date.now()}`;
          console.log("Generated new householdId:", householdId);
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

      const finalImage = formData.image || "/minimal2.png";

      const response = await fetch("http://localhost:8000/api/rooms/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...formData,
          image: finalImage,
          household_id: householdId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.message || "Failed to add room");
      }

      const data = await response.json();

      toast({
        title: "Success",
        description: "Room added successfully!",
        duration: 5000, // Added duration for consistency
      });

      setRooms([...rooms, data.room]);
      setFormData({ name: "", type: "", image: "" });
    } catch (error: any) {
      console.error("Error adding room:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to add room",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      // Get user info from localStorage
      const storedUser = localStorage.getItem("currentUser");
      const storedMember = localStorage.getItem("currentMember");
      
      let householdId;
      
      if (storedUser) {
        const currentUser = JSON.parse(storedUser);
        householdId = currentUser.householdId;
      } else if (storedMember) {
        const currentMember = JSON.parse(storedMember);
        householdId = currentMember.householdId;
      }

      // If no householdId found, check for a generated one or create a new one
      if (!householdId) {
        console.warn("Missing householdId for delete operation. Checking for generated ID.");
        
        // Check if we have a generated householdId in localStorage
        const generatedHouseholdId = localStorage.getItem("generatedHouseholdId");
        
        if (generatedHouseholdId) {
          console.log("Using previously generated householdId for delete:", generatedHouseholdId);
          householdId = generatedHouseholdId;
        } else {
          throw new Error("Household ID not found. Please login again.");
        }
      }

      const response = await fetch(`http://localhost:8000/api/rooms/delete?room_id=${id}&household_id=${householdId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Failed to delete room");
      }

      const updatedRooms = rooms.filter((room) => room.id !== id);
      setRooms(updatedRooms);

      toast({
        title: "Success",
        description: "Room deleted successfully!",
        duration: 5000, // Added duration for consistency
      });
    } catch (error) {
      console.error("Error deleting room:", error);
      toast({
        title: "Error",
        description: "Failed to delete room",
        variant: "destructive",
      });
    }
  };

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

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <NavigationSidebar />
      <div className="flex-1 ml-[72px]">
        <motion.div initial="hidden" animate="visible" variants={containerVariants} className="p-6">
          <motion.header variants={itemVariants} className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-4">
              {/* <div className="w-10 h-10 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xl">Sy</span>
              </div> */}
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Add New Room</h1>
                <p className="text-sm text-gray-500">Create a new room in your smart home</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="icon" onClick={() => router.back()}>
                <ArrowLeft className="h-6 w-6" />
              </Button>
              <Button variant="ghost" size="icon">
                <User className="h-5 w-5" />
              </Button>
            </div>
          </motion.header>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <motion.div variants={itemVariants}>
              <Card className="bg-white shadow-lg">
                <CardHeader>
                  <CardTitle className="text-2xl font-semibold text-[#00B2FF]">Room Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                      <Label htmlFor="name" className="text-gray-700">
                        Room Name
                      </Label>
                      <Input
                        id="name"
                        placeholder="Enter room name"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                        className="border-[#00B2FF] focus:ring-[#00B2FF]"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="type" className="text-gray-700">
                        Room Type
                      </Label>
                      <Select value={formData.type} onValueChange={(value) => setFormData({ ...formData, type: value })}>
                        <SelectTrigger className="border-[#00B2FF] focus:ring-[#00B2FF]">
                          <SelectValue placeholder="Select room type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="living">Living Room</SelectItem>
                          <SelectItem value="bedroom">Bedroom</SelectItem>
                          <SelectItem value="kitchen">Kitchen</SelectItem>
                          <SelectItem value="bathroom">Bathroom</SelectItem>
                          <SelectItem value="office">Office</SelectItem>
                          <SelectItem value="garage">Garage</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label className="text-gray-700">Room Image</Label>
                      <div className="border-2 border-dashed border-[#00B2FF] rounded-lg p-8 text-center hover:bg-blue-50 transition-colors">
                        <Upload className="w-12 h-12 mx-auto mb-4 text-[#00B2FF]" />
                        <div className="space-y-2">
                          <p className="text-sm text-gray-600">Drag and drop an image, or click to select</p>
                          <Input
                            type="file"
                            className="hidden"
                            accept="image/*"
                            onChange={handleImageChange}
                          />
                          <Button
                            type="button"
                            variant="outline"
                            onClick={() => {
                              const fileInput = document.querySelector('input[type="file"]');
                              if (fileInput && fileInput instanceof HTMLInputElement) {
                                fileInput.click();
                              }
                            }}
                            className="border-[#00B2FF] text-[#00B2FF] hover:bg-[#00B2FF] hover:text-white"
                          >
                            Select Image
                          </Button>
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-4">
                      <Button
                        type="button"
                        variant="outline"
                        className="flex-1 border-[#00B2FF] text-[#00B2FF] hover:bg-[#00B2FF] hover:text-white"
                        onClick={() => router.push("/rooms")}
                      >
                        Cancel
                      </Button>
                      <Button
                        type="submit"
                        className="flex-1 bg-[#00B2FF] hover:bg-[#00B2FF]/90"
                        disabled={isLoading}
                      >
                        {isLoading ? "Adding..." : "Add Room"}
                      </Button>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={itemVariants} className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-800">Current Rooms</h2>
              <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {rooms.map((room) => (
                  <motion.div key={room.id} variants={itemVariants}>
                    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
                      <div className="relative h-40">
                        <Image
                          src={room.image || "/minimal2.png"}
                          alt={room.name}
                          layout="fill"
                          objectFit="cover"
                        />
                      </div>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-medium text-lg text-gray-800">{room.name}</h3>
                            <p className="text-sm text-gray-500 capitalize">{room.type}</p>
                          </div>
                          <Button variant="ghost" size="icon" onClick={() => handleDelete(room.id)}>
                            <Trash2 className="h-5 w-5 text-red-500" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </motion.div>
              {rooms.length === 0 && (
                <motion.div variants={itemVariants}>
                  <Card className="p-6 text-center">
                    <Home className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                    <h3 className="text-lg font-semibold text-gray-700 mb-2">No rooms added yet</h3>
                    <p className="text-gray-500">Start by adding your first room above</p>
                  </Card>
                </motion.div>
              )}
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}