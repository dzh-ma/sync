import React, { useState, useEffect } from "react"
import { Card, CardContent } from "../../components/ui/card"
import { Button } from "../../components/ui/button"
import { motion } from "framer-motion"
import { ArrowLeft, Users, Settings, Shield } from "lucide-react"
import { useNavigate, useParams } from "react-router-dom"

interface FamilyMember {
  id: string
  name: string
  email: string
  role: string
  avatar?: string
}

export default function ManageProfilesPage() {
  const navigate = useNavigate()
  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([])

  useEffect(() => {
    const storedMembers = JSON.parse(localStorage.getItem("familyMembers") || "[]")
    setFamilyMembers(storedMembers)
  }, [])

  return (
    <div className="p-6 min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
        <header className="flex justify-between items-center mb-8">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
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
        {familyMembers.map((member, index) => (
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
                      <img
                        src={member.avatar || "/placeholder.svg"}
                        alt={member.name}
                        className="rounded-full object-cover w-full h-full"
                      />
                    ) : (
                      <div className="w-full h-full bg-gray-100 rounded-full flex items-center justify-center">
                        <span className="text-2xl font-semibold text-gray-500">{member.name[0]}</span>
                      </div>
                    )}
                  </div>
                  <h3 className="font-semibold text-lg mb-1">{member.name}</h3>
                  <p className="text-sm text-gray-500 mb-2">
                    {member.role.charAt(0).toUpperCase() + member.role.slice(1)}
                  </p>
                  <p className="text-sm text-gray-500 mb-4">{member.email}</p>
                  <div className="grid grid-cols-2 gap-3 w-full">
                    <Button
                      variant="outline"
                      className="w-full text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF]/10"
                      onClick={() => navigate(`/manage-profiles/${member.id}/details`)}
                    >
                      <Settings className="w-4 h-4 mr-2" />
                      Manage Details
                    </Button>
                    <Button
                      className="w-full bg-[#00B2FF] hover:bg-[#00B2FF]/90"
                      onClick={() => navigate(`/manage-profiles/${member.id}/access`)}
                    >
                      <Shield className="w-4 h-4 mr-2" />
                      Manage Access
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}
