"use client"

import type React from "react"
import Image from "next/image"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import Link from "next/link"
import { Mail } from "lucide-react"
import { toast } from "@/components/ui/use-toast"
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function HouseholdLoginPage() {
  const router = useRouter()
  const [formData, setFormData] = useState({
    email: "",
    pin: ["", "", "", ""]
  })
  const [isLoading, setIsLoading] = useState(false)

  const handlePinChange = (index: number, value: string) => {
    if (value.length > 1) return
    const newPin = [...formData.pin]
    newPin[index] = value
    setFormData({ ...formData, pin: newPin })

    // Auto-focus next input
    if (value && index < 3) {
      const nextInput = document.getElementById(`pin-${index + 1}`)
      nextInput?.focus()
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Join PIN array into a single string
      const pinString = formData.pin.join("")
      
      console.log('Sending login request:', {
        email: formData.email,
        pin: pinString
      })

      const response = await axios.post(`${API_URL}/api/household-login`, {
        email: formData.email,
        pin: pinString
      })
      
      console.log("Login response:", response.data);

      // Set a flag for fresh login to clear previous data
      localStorage.setItem("freshLogin", "true");
      
      // Remove any previously generated household ID
      localStorage.removeItem("generatedHouseholdId");
      
      // Make sure we have a household ID
      const householdId = response.data.household_id || `household-member-${Date.now()}`;

      // Check if we have member_id to fetch permissions
      let permissions = response.data.permissions || {};
      
      if (response.data.member_id && !response.data.permissions) {
        try {
          // Fetch latest permissions from API
          const permissionsResponse = await axios.get(`${API_URL}/api/permissions/${response.data.member_id}`);
          if (permissionsResponse.data) {
            console.log("Fetched permissions from API:", permissionsResponse.data);
            permissions = permissionsResponse.data;
          }
        } catch (permError) {
          console.error("Failed to fetch permissions:", permError);
          // Continue with empty permissions object
        }
      }
      
      console.log("Final permissions to store:", permissions);

      // Store member data in localStorage
      localStorage.setItem(
        "currentMember",
        JSON.stringify({
          id: response.data.member_id,
          type: "member",
          email: response.data.email,
          name: response.data.name,
          accountType: response.data.account_type,
          householdId: householdId,
          permissions: permissions
        })
      )

      toast({
        title: "Login Successful",
        description: "Welcome back to your smart home dashboard!",
      })

      router.push("/dashboard")
    } catch (error: any) {
      console.error("Login error:", error);
      const errorMessage =
        error.response?.data?.detail?.message ||
        error.message ||
        "An error occurred. Please try again."
      
      toast({
        title: "Login Failed",
        description: errorMessage,
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex lg:flex-1 relative">
        <Image
          src="/Login1.png"
          alt="Smart Home"
          fill
          className="object-cover"
        />
        <div className="absolute inset-0 bg-black/20" />
        <div className="absolute bottom-20 left-10 text-white">
          <h1 className="text-5xl font-bold mb-4">
            <span className="text-[#00B2FF]">SYNC</span> your Home,
            <br />
            Save energy,
            <br />
            and live smarter.
          </h1>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          <div className="flex justify-end mb-8">
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold bg-[#00B2FF] text-white px-3 py-1 rounded-full">
                Sy<span className="text-[#FFB800]">nc</span>
              </span>
            </div>
          </div>

          <div className="mb-8">
            <h2 className="text-2xl font-semibold">Welcome,</h2>
            <p className="text-gray-600">Household Member</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium">Enter your Email</label>
              <div className="relative">
                <Input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="pl-10"
                  placeholder="Enter your Email"
                  required
                />
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">PIN</label>
              <div className="flex justify-between gap-4">
                {[0, 1, 2, 3].map((i) => (
                  <Input
                    key={i}
                    id={`pin-${i}`}
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={1}
                    value={formData.pin[i]}
                    onChange={(e) => handlePinChange(i, e.target.value)}
                    className="w-16 h-16 text-center text-2xl"
                    required
                  />
                ))}
              </div>
            </div>

            <Button 
              type="submit" 
              className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg"
              disabled={isLoading || formData.pin.some(p => !p)}
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </Button>

            <div className="text-center">
              <Link href="/auth/login" className="text-[#00B2FF] hover:underline text-sm">
                ← Back to Admin Login
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

