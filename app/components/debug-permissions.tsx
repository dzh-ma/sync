"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function DebugPermissions() {
  const [adminUser, setAdminUser] = useState<any>(null)
  const [memberUser, setMemberUser] = useState<any>(null)

  useEffect(() => {
    const storedUser = localStorage.getItem("currentUser")
    const storedMember = localStorage.getItem("currentMember")
    
    if (storedUser) {
      setAdminUser(JSON.parse(storedUser))
    }
    
    if (storedMember) {
      setMemberUser(JSON.parse(storedMember))
    }
  }, [])

  return (
    <Card className="mb-6">
      <CardHeader>
        <CardTitle>Debug Permissions</CardTitle>
      </CardHeader>
      <CardContent>
        {adminUser && (
          <div className="mb-4">
            <h3 className="font-bold">Admin User:</h3>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
              {JSON.stringify(adminUser, null, 2)}
            </pre>
          </div>
        )}
        
        {memberUser && (
          <div>
            <h3 className="font-bold">Member User:</h3>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-auto">
              {JSON.stringify(memberUser, null, 2)}
            </pre>
          </div>
        )}
        
        {!adminUser && !memberUser && (
          <p>No user data found in localStorage</p>
        )}
      </CardContent>
    </Card>
  )
} 