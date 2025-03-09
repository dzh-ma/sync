"use client"

import React from "react"
import { NavigationSidebar } from "../components/navigation-sidebar"
import { Button } from "../../components/ui/button"
import { Plus, User, Home } from "lucide-react"
import { useState } from "react"
import { RoomCard } from "./room-card"
import { AddRoomDialog } from "./add-room-dialog"
import { Card } from "../../components/ui/card"
import Link from "next/link"

const initialRooms = [
  {
    id: 1,
    name: "Living Room",
    image: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/IMG_0697-MRkZkq9qJMNVm20BYSDpYOdkYHt3pF.jpeg",
  },
  {
    id: 2,
    name: "Bedroom",
    image: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/IMG_0697-MRkZkq9qJMNVm20BYSDpYOdkYHt3pF.jpeg",
  },
  {
    id: 3,
    name: "Laundry Room",
    image: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/IMG_0697-MRkZkq9qJMNVm20BYSDpYOdkYHt3pF.jpeg",
  },
  {
    id: 4,
    name: "Garage",
    image: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/IMG_0697-MRkZkq9qJMNVm20BYSDpYOdkYHt3pF.jpeg",
  },
  {
    id: 5,
    name: "Kitchen",
    image: "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/IMG_0697-MRkZkq9qJMNVm20BYSDpYOdkYHt3pF.jpeg",
  },
]

export default function RoomsPage() {
  const [rooms, setRooms] = useState(initialRooms)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const handleAddRoom = (newRoom: { name: string; image: string }) => {
    setRooms([...rooms, { id: rooms.length + 1, ...newRoom }])
    setIsDialogOpen(false)
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
                <RoomCard key={room.id} name={room.name} image={room.image} />
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

