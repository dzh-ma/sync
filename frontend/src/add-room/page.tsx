import React from "react";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../components/ui/select";
import { User, Upload, Trash2, ArrowLeft, Home } from "lucide-react";
import { NavigationSidebar } from "../../components/navigation-sidebar";

interface Room {
  id: number;
  name: string;
  type: string;
  image: string;
}

export default function AddRoomPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    type: "",
    image: "",
  });
  const [rooms, setRooms] = useState<Room[]>([]);

  useEffect(() => {
    const storedRooms = JSON.parse(localStorage.getItem("rooms") || "[]");
    setRooms(storedRooms);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newRoom = {
      id: Date.now(),
      ...formData,
    };
    const updatedRooms = [...rooms, newRoom];
    localStorage.setItem("rooms", JSON.stringify(updatedRooms));
    setRooms(updatedRooms);
    setFormData({ name: "", type: "", image: "" });
  };

  const handleDelete = (id: number) => {
    const updatedRooms = rooms.filter((room) => room.id !== id);
    localStorage.setItem("rooms", JSON.stringify(updatedRooms));
    setRooms(updatedRooms);
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
    <div className="w-10 h-10 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center">
    <span className="text-white font-bold text-xl">Sy</span>
    </div>
    <div>
    <h1 className="text-2xl font-bold text-gray-800">Add New Room</h1>
    <p className="text-sm text-gray-500">Create a new room in your smart home</p>
    </div>
    </div>
    <div className="flex items-center gap-2">
    <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
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
    onChange={(e) => {
      const file = e.target.files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onloadend = () => {
          setFormData({ ...formData, image: reader.result as string });
        };
        reader.readAsDataURL(file);
      }
    }}
    />
      <Button
      type="button"
      variant="outline"
      onClick={() => document.querySelector('input[type="file"]')?.click()}
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
      onClick={() => navigate("/")}
    >
      Cancel
      </Button>
      <Button type="submit" className="flex-1 bg-[#00B2FF] hover:bg-[#00B2FF]/90">
      Add Room
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
            <img 
            src={room.image || "/placeholder.svg"} 
            alt={room.name} 
            className="w-full h-full object-cover"
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
