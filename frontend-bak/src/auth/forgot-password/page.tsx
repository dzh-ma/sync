"use client"

// FIX: Errors
import React from "react"

import { useState, useRef, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "../../../components/ui/button"
import { Input } from "../../../components/ui/input"
import { toast } from "../../../components/ui/use-toast"
import { ArrowLeft, Mail, Lock } from "lucide-react"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "../../../components/ui/card"

export default function ForgotPasswordPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [email, setEmail] = useState("")
  const [otp, setOtp] = useState(["", "", "", "", "", ""])
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const otpRefs = useRef<(HTMLInputElement | null)[]>([])

  useEffect(() => {
    otpRefs.current = otpRefs.current.slice(0, 6)
  }, [])

  const handleSendOTP = (e: React.FormEvent) => {
    e.preventDefault()
    toast({
      title: "OTP Sent",
      description: "Please check your email for the OTP.",
    })
    setStep(2)
  }

  const handleVerifyOTP = (e: React.FormEvent) => {
    e.preventDefault()
    if (otp.join("") === "123456") {
      setStep(3)
    } else {
      toast({
        title: "Invalid OTP",
        description: "Please enter the correct OTP.",
        variant: "destructive",
      })
    }
  }

  const handleResetPassword = (e: React.FormEvent) => {
    e.preventDefault()
    if (newPassword !== confirmPassword) {
      toast({
        title: "Passwords do not match",
        description: "Please make sure your passwords match.",
        variant: "destructive",
      })
      return
    }
    toast({
      title: "Password Reset Successful",
      description: "Your password has been reset. Please log in with your new password.",
    })
    navigate("/auth/login")
  }

  const handleOtpChange = (index: number, value: string) => {
    if (value.length > 1) return
    const newOtp = [...otp]
    newOtp[index] = value
    setOtp(newOtp)
    if (value && index < 5) {
      otpRefs.current[index + 1]?.focus()
    }
  }

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      otpRefs.current[index - 1]?.focus()
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader>
          <div className="flex justify-between items-center mb-4">
            <Link href="/auth/login" className="text-[#00B2FF] hover:underline flex items-center">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Login
            </Link>
            <div className="w-10 h-10 bg-[#00B2FF] rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-xl">Sy</span>
            </div>
          </div>
          <CardTitle className="text-2xl font-bold text-center text-gray-900">Reset your password</CardTitle>
          <CardDescription className="text-center text-gray-500">
            {step === 1 && "Enter your email to receive a one-time password"}
            {step === 2 && "Enter the OTP sent to your email"}
            {step === 3 && "Create a new password for your account"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {step === 1 && (
            <form onSubmit={handleSendOTP} className="space-y-4">
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <Input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-10 border-gray-300 focus:border-[#00B2FF] focus:ring-[#00B2FF]"
                  required
                />
              </div>
              <Button type="submit" className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 text-white">
                Send OTP
              </Button>
            </form>
          )}
          {step === 2 && (
            <form onSubmit={handleVerifyOTP} className="space-y-4">
              <div className="flex justify-between gap-2">
                {otp.map((digit, index) => (
                  <Input
                    key={index}
                    type="text"
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={1}
                    className="w-12 h-12 text-center text-2xl border-gray-300 focus:border-[#00B2FF] focus:ring-[#00B2FF]"
                    value={digit}
                    onChange={(e) => handleOtpChange(index, e.target.value)}
                    onKeyDown={(e) => handleOtpKeyDown(index, e)}
                    ref={(el) => (otpRefs.current[index] = el)}
                  />
                ))}
              </div>
              <Button type="submit" className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 text-white">
                Verify OTP
              </Button>
            </form>
          )}
          {step === 3 && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <Input
                  type="password"
                  placeholder="New Password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="pl-10 border-gray-300 focus:border-[#00B2FF] focus:ring-[#00B2FF]"
                  required
                />
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <Input
                  type="password"
                  placeholder="Confirm New Password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="pl-10 border-gray-300 focus:border-[#00B2FF] focus:ring-[#00B2FF]"
                  required
                />
              </div>
              <Button type="submit" className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 text-white">
                Reset Password
              </Button>
            </form>
          )}
        </CardContent>
        <CardFooter className="text-center">
          <p className="text-sm text-gray-600">
            Remember your password?{" "}
            <Link href="/auth/login" className="text-[#00B2FF] hover:underline">
              Login here
            </Link>
          </p>
        </CardFooter>
      </Card>
    </div>
  )
}

