"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { motion } from "framer-motion"
import { ArrowLeft, Bell, Zap, Clock, BarChart2, Database, Smartphone } from "lucide-react"
import { useRouter } from "next/navigation"
import { toast } from "@/components/ui/use-toast"

interface FamilyMember {
  id: string
  name: string
  email: string
  account_type: string
  permissions?: {
    notifications: boolean
    energyAlerts: boolean
    addAutomation: boolean
    statisticalData: boolean
    deviceControl: boolean
    roomControl: boolean
  }
}

interface Permissions {
  notifications: boolean
  energyAlerts: boolean
  addAutomation: boolean
  statisticalData: boolean
  deviceControl: boolean
  roomControl: boolean
}

export default function ManageProfileAccessPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const memberId = params.id
  const [member, setMember] = useState<FamilyMember | null>(null)
  const [permissions, setPermissions] = useState<Permissions>({
    notifications: true,
    energyAlerts: true,
    addAutomation: false,
    statisticalData: false,
    deviceControl: true,
    roomControl: false
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

      // Use environment variable for API URL
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

      // Fetch member details
      const response = await fetch(`${API_URL}/api/household-members?household_id=${currentUser.householdId}`)
      
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
      
      // If member has permissions, use them
      if (member.permissions) {
        console.log("Using permissions from member:", member.permissions)
        setPermissions(member.permissions)
      } else {
        // Otherwise fetch permissions separately
        const permissionsResponse = await fetch(`${API_URL}/api/permissions/${memberId}`)
        
        if (permissionsResponse.ok) {
          const permissionsData = await permissionsResponse.json()
          console.log("Fetched permissions:", permissionsData)
          
          // Merge with default permissions to ensure all fields exist
          setPermissions(prev => ({
            ...prev,
            ...permissionsData
          }))
        } else {
          console.error("Failed to fetch permissions:", await permissionsResponse.text())
        }
      }
      
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

  const handleSaveChanges = async () => {
    try {
      const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}")
      
      console.log("Saving permissions:", permissions)
      
      // Use environment variable for API URL
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      
      // Prepare the payload
      const payload = {
        member_id: memberId,
        household_id: currentUser.householdId,
        permissions: permissions
      }
      
      console.log("Sending permission update payload:", payload)
      
      const response = await fetch(`${API_URL}/api/permissions/update`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error("Failed to update permissions:", errorText)
        
        // More specific error message based on status code
        if (response.status === 404) {
          throw new Error("Member not found")
        } else if (response.status === 403) {
          throw new Error("You don't have permission to update this member")
        } else if (response.status === 422) {
          throw new Error("Invalid permission format")
        } else {
          throw new Error(`Server error (${response.status}): Failed to update permissions`)
        }
      }
      
      toast({
        title: "Success",
        description: "Permissions updated successfully",
      })
      
      // Update local storage for the user if it exists there
      try {
        const storedMember = localStorage.getItem("currentMember")
        if (storedMember) {
          const memberData = JSON.parse(storedMember)
          if (memberData.id === memberId) {
            // Update permissions in localStorage for this member
            memberData.permissions = permissions
            localStorage.setItem("currentMember", JSON.stringify(memberData))
            console.log("Updated permissions in localStorage")
          }
        }
      } catch (e) {
        console.error("Error updating localStorage permissions:", e)
      }
      
      router.push("/profile")
    } catch (error: any) {
      console.error("Error updating permissions:", error)
      toast({
        title: "Error",
        description: error.message || "Failed to update permissions",
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
              <h1 className="text-2xl font-bold text-gray-800">Manage Access</h1>
              <p className="text-sm text-gray-500">
                {member.name} • {member.account_type}
              </p>
            </div>
          </div>
        </header>
      </motion.div>

      <div className="grid gap-6 max-w-2xl mx-auto">
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
                    <p className="text-sm text-gray-500">Receive app notifications</p>
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
                    <p className="text-sm text-gray-500">Get energy usage alerts</p>
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
                    <p className="font-medium">Statistical Data</p>
                    <p className="text-sm text-gray-500">View usage statistics</p>
                  </div>
                </div>
                <Switch
                  checked={permissions.statisticalData}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, statisticalData: checked })}
                  className="data-[state=checked]:bg-[#00B2FF]"
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Database className="h-5 w-5 text-[#00B2FF]" />
                  <div>
                    <p className="font-medium">Room Control</p>
                    <p className="text-sm text-gray-500">Control room settings</p>
                  </div>
                </div>
                <Switch
                  checked={permissions.roomControl}
                  onCheckedChange={(checked) => setPermissions({ ...permissions, roomControl: checked })}
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

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Button className="w-full bg-[#00B2FF] hover:bg-[#00B2FF]/90" onClick={handleSaveChanges}>
            Save Changes
          </Button>
        </motion.div>
      </div>
    </div>
  )
}

