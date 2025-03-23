"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { ArrowLeft, Users, Settings, Shield } from "lucide-react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { toast } from "@/components/ui/use-toast"

interface FamilyMember {
  id: string
  name: string
  email: string
  account_type: string
  avatar?: string
  permissions?: Record<string, boolean>
}

export default function ManageProfilesPage() {
  const router = useRouter()
  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchFamilyMembers()
  }, [])

  const fetchFamilyMembers = async () => {
    try {
      const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}")
      if (!currentUser.householdId) {
        toast({
          title: "Error",
          description: "Household ID not found. Please login again.",
          variant: "destructive",
        })
        return
      }

      const response = await fetch(`http://localhost:8000/api/household-members?household_id=${currentUser.householdId}`)
      
      if (!response.ok) {
        throw new Error("Failed to fetch household members")
      }
      
      const data = await response.json()
      setFamilyMembers(data)
    } catch (error: any) {
      console.error("Error fetching family members:", error)
      toast({
        title: "Error",
        description: error.message || "Failed to load family members",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="p-6 min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <header className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.back()}>
              <ArrowLeft className="h-6 w-6" />
            </Button>
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                <Users className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Manage Profiles</h1>
                <p className="text-sm text-gray-500">Manage access and permissions for family members</p>
              </div>
            </div>
          </div>
        </header>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {isLoading ? (
          <p className="col-span-full text-center py-8">Loading family members...</p>
        ) : familyMembers.length === 0 ? (
          <div className="col-span-full text-center py-8">
            <p className="text-gray-500 mb-4">No family members found</p>
            <Button 
              className="bg-[#00B2FF] hover:bg-[#00B2FF]/90"
              onClick={() => router.push("/create-profile")}
            >
              Add Family Member
            </Button>
          </div>
        ) : (
          familyMembers.map((member, index) => (
            <motion.div
              key={member.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="overflow-hidden hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="flex flex-col items-center text-center">
                    <div className="relative w-24 h-24 mb-4">
                      {member.avatar ? (
                        <Image
                          src={member.avatar || "/placeholder.svg"}
                          alt={member.name}
                          fill
                          className="rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full bg-gray-100 rounded-full flex items-center justify-center">
                          <span className="text-2xl font-semibold text-gray-500">{member.name[0]}</span>
                        </div>
                      )}
                    </div>
                    <h3 className="font-semibold text-lg mb-1">{member.name}</h3>
                    <p className="text-sm text-gray-500 mb-2">
                      {member.account_type?.charAt(0).toUpperCase() + member.account_type?.slice(1) || "Member"}
                    </p>
                    <p className="text-sm text-gray-500 mb-4">{member.email}</p>
                    <div className="grid grid-cols-2 gap-3 w-full">
                      <Button
                        variant="outline"
                        className="w-full text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF]/10"
                        onClick={() => router.push(`/manage-profiles/${member.id}/details`)}
                      >
                        <Settings className="w-4 h-4 mr-2" />
                        Manage Details
                      </Button>
                      <Button
                        className="w-full bg-[#00B2FF] hover:bg-[#00B2FF]/90"
                        onClick={() => router.push(`/manage-profiles/${member.id}/access`)}
                      >
                        <Shield className="w-4 h-4 mr-2" />
                        Manage Access
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))
        )}
      </motion.div>
    </div>
  )
}

