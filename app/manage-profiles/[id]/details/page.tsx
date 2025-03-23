"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { motion } from "framer-motion"
import { ArrowLeft, User, Key, Trash2, Mail } from "lucide-react"
import { useRouter } from "next/navigation"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { toast } from "@/components/ui/use-toast"
import { use } from "react"

interface FamilyMember {
  id: string
  name: string
  email: string
  account_type: string
  pin?: string
}

export default function ManageProfileDetailsPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  // Use React.use() to unwrap the params object
  const unwrappedParams = use(params)
  const memberId = unwrappedParams.id
  
  const [member, setMember] = useState<FamilyMember | null>(null)
  const [isChangePinOpen, setIsChangePinOpen] = useState(false)
  const [newPin, setNewPin] = useState(["", "", "", ""])
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    account_type: "",
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchMemberDetails()
  }, [memberId])

  const fetchMemberDetails = async () => {
    try {
      const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}")
      if (!currentUser.householdId) {
        toast({
          title: "Error",
          description: "Household ID not found. Please login again.",
          variant: "destructive",
        })
        router.push("/auth/login")
        return
      }

      // Fetch member details
      const response = await fetch(`http://localhost:8000/api/household-members?household_id=${currentUser.householdId}`)
      
      if (!response.ok) {
        throw new Error("Failed to fetch household members")
      }
      
      const members = await response.json()
      const member = members.find((m: FamilyMember) => m.id === memberId)
      
      if (!member) {
        toast({
          title: "Error",
          description: "Member not found",
          variant: "destructive",
        })
        router.push("/manage-profiles")
        return
      }
      
      setMember(member)
      setFormData({
        name: member.name,
        email: member.email,
        account_type: member.account_type,
      })
      
    } catch (error: any) {
      console.error("Error fetching member details:", error)
      toast({
        title: "Error",
        description: error.message || "Failed to load member details",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handlePinChange = (index: number, value: string) => {
    if (value.length > 1) return
    const newPinArray = [...newPin]
    newPinArray[index] = value
    setNewPin(newPinArray)

    if (value !== "" && index < 3) {
      const nextInput = document.getElementById(`pin-${index + 1}`)
      nextInput?.focus()
    }
  }

  const handleSaveChanges = async () => {
    try {
      const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}")
      
      const response = await fetch(`http://localhost:8000/api/household-members/update`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          member_id: memberId,
          household_id: currentUser.householdId,
          ...formData
        }),
      })
      
      if (!response.ok) {
        throw new Error("Failed to update member details")
      }
      
      toast({
        title: "Success",
        description: "Member details updated successfully",
      })
      
      router.push("/profile")
    } catch (error: any) {
      console.error("Error updating member details:", error)
      toast({
        title: "Error",
        description: error.message || "Failed to update member details",
        variant: "destructive",
      })
    }
  }

  const handleSavePin = async () => {
    try {
      const pin = newPin.join("")
      if (pin.length !== 4) {
        toast({
          title: "Error",
          description: "PIN must be 4 digits",
          variant: "destructive",
        })
        return
      }
      
      const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}")
      
      const response = await fetch(`http://localhost:8000/api/household-members/update-pin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          member_id: memberId,
          household_id: currentUser.householdId,
          pin: pin
        }),
      })
      
      if (!response.ok) {
        throw new Error("Failed to update PIN")
      }
      
      toast({
        title: "Success",
        description: "PIN updated successfully",
      })
      
      setIsChangePinOpen(false)
      setNewPin(["", "", "", ""])
    } catch (error: any) {
      console.error("Error updating PIN:", error)
      toast({
        title: "Error",
        description: error.message || "Failed to update PIN",
        variant: "destructive",
      })
    }
  }

  const handleDeleteProfile = async () => {
    if (!confirm(`Are you sure you want to delete ${member?.name}'s profile? This action cannot be undone.`)) {
      return
    }
    
    try {
      const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}")
      
      const response = await fetch(`http://localhost:8000/api/household-members/delete?member_id=${memberId}&household_id=${currentUser.householdId}`, {
        method: "DELETE",
      })
      
      if (!response.ok) {
        throw new Error("Failed to delete profile")
      }
      
      toast({
        title: "Success",
        description: "Profile deleted successfully",
      })
      
      router.push("/manage-profiles")
    } catch (error: any) {
      console.error("Error deleting profile:", error)
      toast({
        title: "Error",
        description: error.message || "Failed to delete profile",
        variant: "destructive",
      })
    }
  }

  if (isLoading) {
    return (
      <div className="p-6 min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <p>Loading profile details...</p>
      </div>
    )
  }

  if (!member) return null

  return (
    <div className="p-6 min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <header className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.back()}>
              <ArrowLeft className="h-6 w-6" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Manage Details</h1>
              <p className="text-sm text-gray-500">{member.name}</p>
            </div>
          </div>
        </header>
      </motion.div>

      <div className="grid gap-6 max-w-2xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">Role</Label>
                <Select
                  value={formData.account_type}
                  onValueChange={(value) => setFormData({ ...formData, account_type: value })}
                >
                  <SelectTrigger id="role">
                    <SelectValue placeholder="Select role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="adult">Adult</SelectItem>
                    <SelectItem value="child">Child</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex gap-4"
        >
          <Dialog open={isChangePinOpen} onOpenChange={setIsChangePinOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="flex-1">
                <Key className="w-4 h-4 mr-2" />
                Change PIN
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Change PIN</DialogTitle>
                <DialogDescription>Enter a new 4-digit PIN for this profile.</DialogDescription>
              </DialogHeader>
              <div className="flex justify-center gap-4 py-4">
                {[0, 1, 2, 3].map((i) => (
                  <Input
                    key={i}
                    id={`pin-${i}`}
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={1}
                    className="w-16 h-16 text-2xl text-center"
                    value={newPin[i]}
                    onChange={(e) => handlePinChange(i, e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Backspace" && !newPin[i] && i > 0) {
                        const prevInput = document.getElementById(`pin-${i - 1}`)
                        prevInput?.focus()
                      }
                    }}
                  />
                ))}
              </div>
              <DialogFooter>
                <Button
                  onClick={handleSavePin}
                  disabled={newPin.some((digit) => !digit)}
                  className="w-full bg-[#00B2FF] hover:bg-[#00B2FF]/90"
                >
                  Save PIN
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Button variant="destructive" className="flex-1" onClick={handleDeleteProfile}>
            <Trash2 className="w-4 h-4 mr-2" />
            Delete Profile
          </Button>

          <Button className="flex-1 bg-[#00B2FF] hover:bg-[#00B2FF]/90" onClick={handleSaveChanges}>
            Save Changes
          </Button>
        </motion.div>
      </div>
    </div>
  )
}

