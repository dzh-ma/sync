import React from "react"
import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "../../../../components/ui/card"
import { Button } from "../../../../components/ui/button"
import { Input } from "../../../../components/ui/input"
import { Label } from "../../../../components/ui/label"
import { motion } from "framer-motion"
import { ArrowLeft, User, Key, Trash2, Mail } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../../../components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../../components/ui/select"

interface FamilyMember {
  id: string
  name: string
  email: string
  role: string
  pin?: string
}

export default function ManageProfileDetailsPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [member, setMember] = useState<FamilyMember | null>(null)
  const [isChangePinOpen, setIsChangePinOpen] = useState(false)
  const [newPin, setNewPin] = useState(["", "", "", ""])
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    role: "",
  })

  useEffect(() => {
    const storedMembers = JSON.parse(localStorage.getItem("familyMembers") || "[]")
    const member = storedMembers.find((m: FamilyMember) => m.id === id)
    if (member) {
      setMember(member)
      setFormData({
        name: member.name,
        email: member.email,
        role: member.role,
      })
    }
  }, [id])

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

  const handleSaveChanges = () => {
    const storedMembers = JSON.parse(localStorage.getItem("familyMembers") || "[]")
    const updatedMembers = storedMembers.map((m: FamilyMember) => {
      if (m.id === id) {
        return {
          ...m,
          ...formData,
        }
      }
      return m
    })
    localStorage.setItem("familyMembers", JSON.stringify(updatedMembers))
    navigate("/manage-profiles")
  }

  const handleSavePin = () => {
    const pin = newPin.join("")
    if (pin.length === 4) {
      const storedMembers = JSON.parse(localStorage.getItem("familyMembers") || "[]")
      const updatedMembers = storedMembers.map((m: FamilyMember) => {
        if (m.id === id) {
          return {
            ...m,
            pin,
          }
        }
        return m
      })
      localStorage.setItem("familyMembers", JSON.stringify(updatedMembers))
      setIsChangePinOpen(false)
      setNewPin(["", "", "", ""])
    }
  }

  const handleDeleteProfile = () => {
    const storedMembers = JSON.parse(localStorage.getItem("familyMembers") || "[]")
    const updatedMembers = storedMembers.filter((m: FamilyMember) => m.id !== id)
    localStorage.setItem("familyMembers", JSON.stringify(updatedMembers))
    navigate("/manage-profiles")
  }

  if (!member) return null

  return (
    <div className="p-6 min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <header className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
              <ArrowLeft className="h-6 w-6" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Manage Details</h1>
              <p className="text-sm text-gray-500">
                {member.name} • {member.role}
              </p>
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
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label>Name</Label>
                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <Input
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="pl-10"
                    />
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Email</Label>
                <div className="relative">
                  <Input
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="pl-10"
                  />
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Role</Label>
                <Select value={formData.role} onValueChange={(value) => setFormData({ ...formData, role: value })}>
                  <SelectTrigger>
                    <SelectValue />
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
