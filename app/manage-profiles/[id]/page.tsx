"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Input } from "@/components/ui/input"
import { motion } from "framer-motion"
import { ArrowLeft, Bell, Zap, Clock, BarChart2, Database, History, Smartphone, Trash2, Key } from "lucide-react"
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

interface FamilyMember {
  id: string
  name: string
  email: string
  role: string
  permissions?: {
    notifications: boolean
    energyAlerts: boolean
    addAutomation: boolean
    realTimeMonitoring: boolean
    analyticalData: boolean
    historicalData: boolean
    deviceControl: boolean
  }
  pin?: string
}

export default function ManageProfilePage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [member, setMember] = useState<FamilyMember | null>(null)
  const [permissions, setPermissions] = useState({
    notifications: true,
    energyAlerts: true,
    addAutomation: false,
    realTimeMonitoring: true,
    analyticalData: false,
    historicalData: false,
    deviceControl: true,
  })
  const [isChangePinOpen, setIsChangePinOpen] = useState(false)
  const [newPin, setNewPin] = useState(["", "", "", ""])

  useEffect(() => {
    const storedMembers = JSON.parse(localStorage.getItem("familyMembers") || "[]")
    const member = storedMembers.find((m: FamilyMember) => m.id === params.id)
    if (member) {
      setMember(member)
      if (member.permissions) {
        setPermissions(member.permissions)
      }
    }
  }, [params.id])

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
      if (m.id === params.id) {
        return {
          ...m,
          permissions,
        }
      }
      return m
    })
    localStorage.setItem("familyMembers", JSON.stringify(updatedMembers))
    router.push("/manage-profiles")
  }

  const handleSavePin = () => {
    const pin = newPin.join("")
    if (pin.length === 4) {
      const storedMembers = JSON.parse(localStorage.getItem("familyMembers") || "[]")
      const updatedMembers = storedMembers.map((m: FamilyMember) => {
        if (m.id === params.id) {
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
    const updatedMembers = storedMembers.filter((m: FamilyMember) => m.id !== params.id)
    localStorage.setItem("familyMembers", JSON.stringify(updatedMembers))
    router.push("/manage-profiles")
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
              <h1 className="text-2xl font-bold text-gray-800">Manage Access</h1>
              <p className="text-sm text-gray-500">
                {member.name} • {member.role}
              </p>
            </div>
          </div>
        </header>
      </motion.div>

      <div className="grid gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <Card>
            <CardHeader>
              <CardTitle>Access Permissions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Bell className="h-5 w-5 text-[#00B2FF]" />
                  <div>
                    <p className="font-medium">Notifications</p>
                    <p className="text-sm text-gray-500">Receive system notifications</p>
                  </div>
                </div>
                <Switch
                  checked={permissions.notifications}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, notifications: checked })}
                  className="data-[state=checked]:bg-[#00B2FF]"
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Zap className="h-5 w-5 text-[#00B2FF]" />
                  <div>
                    <p className="font-medium">Energy Alerts</p>
                    <p className="text-sm text-gray-500">Receive energy consumption alerts</p>
                  </div>
                </div>
                <Switch
                  checked={permissions.energyAlerts}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, energyAlerts: checked })}
                  className="data-[state=checked]:bg-[#00B2FF]"
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Clock className="h-5 w-5 text-[#00B2FF]" />
                  <div>
                    <p className="font-medium">Add Automation</p>
                    <p className="text-sm text-gray-500">Create and modify automations</p>
                  </div>
                </div>
                <Switch
                  checked={permissions.addAutomation}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, addAutomation: checked })}
                  className="data-[state=checked]:bg-[#00B2FF]"
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <BarChart2 className="h-5 w-5 text-[#00B2FF]" />
                  <div>
                    <p className="font-medium">Real Time Monitoring</p>
                    <p className="text-sm text-gray-500">View live device status</p>
                  </div>
                </div>
                <Switch
                  checked={permissions.realTimeMonitoring}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, realTimeMonitoring: checked })}
                  className="data-[state=checked]:bg-[#00B2FF]"
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Database className="h-5 w-5 text-[#00B2FF]" />
                  <div>
                    <p className="font-medium">Analytical Data</p>
                    <p className="text-sm text-gray-500">Access usage analytics</p>
                  </div>
                </div>
                <Switch
                  checked={permissions.analyticalData}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, analyticalData: checked })}
                  className="data-[state=checked]:bg-[#00B2FF]"
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <History className="h-5 w-5 text-[#00B2FF]" />
                  <div>
                    <p className="font-medium">Historical Data</p>
                    <p className="text-sm text-gray-500">View past usage data</p>
                  </div>
                </div>
                <Switch
                  checked={permissions.historicalData}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, historicalData: checked })}
                  className="data-[state=checked]:bg-[#00B2FF]"
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Smartphone className="h-5 w-5 text-[#00B2FF]" />
                  <div>
                    <p className="font-medium">Device Control</p>
                    <p className="text-sm text-gray-500">Control smart devices</p>
                  </div>
                </div>
                <Switch
                  checked={permissions.deviceControl}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, deviceControl: checked })}
                  className="data-[state=checked]:bg-[#00B2FF]"
                />
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

