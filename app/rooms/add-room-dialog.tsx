"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface AddRoomDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onAdd: (room: { name: string; type: string; image: string }) => void
}

export function AddRoomDialog({ open, onOpenChange, onAdd }: AddRoomDialogProps) {
  const [name, setName] = useState("")
  const [type, setType] = useState("")
  const [image, setImage] = useState("https://hebbkx1anhila5yf.public.blob.vercel-storage.com/IMG_0697-MRkZkq9qJMNVm20BYSDpYOdkYHt3pF.jpeg")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    
    if (name && type) {
      onAdd({ name, type, image })
      setName("")
      setType("")
      setIsLoading(false)
    } else {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add New Room</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Room Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter room name"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="type">Room Type</Label>
            <Select value={type} onValueChange={setType} required>
              <SelectTrigger id="type">
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
            <Label htmlFor="image">Image URL (Optional)</Label>
            <Input
              id="image"
              value={image}
              onChange={(e) => setImage(e.target.value)}
              placeholder="Enter image URL"
            />
          </div>
          <Button type="submit" className="w-full bg-[#00B2FF] hover:bg-[#00B2FF]/90" disabled={isLoading}>
            {isLoading ? "Adding..." : "Add Room"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}

