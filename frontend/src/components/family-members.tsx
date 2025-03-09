"use client"

import React from "react"
import { useEffect, useState } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/card"
import { Avatar, AvatarFallback } from "../../components/ui/avatar"
import { Button } from "../../components/ui/button"
import Link from "next/link"
import './FamilyMembers.css' // Import the CSS file

interface FamilyMember {
  id: string
  name: string
  email: string
  role: string
}

export function FamilyMembers() {
  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([])

  useEffect(() => {
    const storedMembers = JSON.parse(localStorage.getItem("familyMembers") || "[]")
    setFamilyMembers(storedMembers)
  }, [])

  return (
    <Card className="card-containerF">
      <CardHeader className="card-headerF">
        <CardTitle className="card-titleF">Family Members</CardTitle>
        <Link href="/profile">
          <Button variant="ghost" className="h-8 w-8 p-0">
            <span className="sr-only">Manage family members</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              className="button-iconF"
            >
              <path d="M12 5v14M5 12h14" />
            </svg>
          </Button>
        </Link>
      </CardHeader>
      <CardContent className="card-contentF">
        <div className="space-y-4">
          {familyMembers.length === 0 ? (
            <p className="text-sm text-muted-foreground">No family members added yet.</p>
          ) : (
            familyMembers.map((member) => (
              <div key={member.id} className="family-memberF">
                <Avatar>
                  <AvatarFallback>{member.name[0]}</AvatarFallback>
                </Avatar>
                <div>
                  <p className="family-member-nameF">{member.name}</p>
                  <p className="family-member-roleF">{member.role}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}
