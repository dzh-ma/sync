"use client"

import Image from "next/image"
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { Eye, EyeOff, Mail } from "lucide-react";
import { toast } from "@/components/ui/use-toast";
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function LoginPage() {
  const router = useRouter();
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [isLoading, setIsLoading] = useState(false);
  const [isForgotPassword, setIsForgotPassword] = useState(false);
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.email || !formData.password) {
      toast({
        title: "Invalid Input",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/login`, formData);
      const userData = response.data;

      // Set a flag for fresh login to clear previous data
      localStorage.setItem("freshLogin", "true");
      
      // Remove any previously generated household ID
      localStorage.removeItem("generatedHouseholdId");

      // Make sure we have a household ID
      const householdId = userData.household_id || `household-${Date.now()}`;

      // Use permissions directly from the backend if they exist
      // Do not set default permissions
      console.log("Backend user data:", userData);
      
      // Define admin default permissions if none provided from backend
      const adminDefaultPermissions = {
        notifications: true,
        energyAlerts: true,
        addAutomation: true,
        statisticalData: true,
        deviceControl: true,
        roomControl: true
      };
      
      // Use permissions from backend or set defaults for admin
      const permissions = userData.permissions || adminDefaultPermissions;
      console.log("Admin permissions to store:", permissions);

      localStorage.setItem(
        "currentUser",
        JSON.stringify({
          id: userData.user_id,
          type: "admin",
          email: userData.admin_email,
          name: userData.firstName || "Admin",
          role: "Admin",
          householdId: householdId,
          permissions: permissions
        })
      );

      router.push("/dashboard");
    } catch (error) {
      const errorMessage =
        (error as any).response?.data?.detail ||
        (error as any).message ||
        "An error occurred. Please try again.";
      toast({
        title: "Login Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = async () => {
    if (!formData.email) {
      toast({
        title: "Invalid Input",
        description: "Please enter your email",
        variant: "destructive",
      });
      return;
    }

    try {
      await axios.post(`${API_URL}/request-forgot-password-otp`, { email: formData.email });
      toast({
        title: "OTP Sent",
        description: "An OTP has been sent to your email",
        variant: "default",
      });
      setIsForgotPassword(true);
    } catch (error) {
      const errorMessage =
        (error as any).response?.data?.detail ||
        (error as any).message ||
        "An error occurred. Please try again.";
      toast({
        title: "Request Failed",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!otp || !newPassword) {
      toast({
        title: "Invalid Input",
        description: "Please fill in all fields",
        variant: "destructive",
      });
      return;
    }

    try {
      // Verify OTP
      await axios.post(`${API_URL}/verify-forgot-password-otp`, { email: formData.email, otp });
      
      // Reset Password
      await axios.post(`${API_URL}/reset-password`, { email: formData.email, password: newPassword });
      toast({
        title: "Password Reset",
        description: "Your password has been reset successfully",
        variant: "default",
      });
      setIsForgotPassword(false);
    } catch (error) {
      const errorMessage =
        (error as any).response?.data?.detail ||
        (error as any).message ||
        "An error occurred. Please try again.";
      toast({
        title: "Reset Failed",
        description: errorMessage,
        variant: "destructive",
      });
    }
  };

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
          <Link href="/auth/signup">
            <Button className="bg-[#FF9500] hover:bg-[#FF9500]/90 text-lg px-8 py-6">
              Sign Up
            </Button>
          </Link>
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
            <p className="text-gray-600">Admin Login</p>
          </div>

          {!isForgotPassword ? (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">Email</label>
                <div className="relative">
                  <Input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="pl-10"
                    placeholder="Enter your email"
                    required
                  />
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Password</label>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="pr-10"
                    placeholder="Enter your password"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-gray-400" />
                    ) : (
                      <Eye className="h-5 w-5 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <div className="flex justify-between items-center">
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  className="text-sm text-[#00B2FF] hover:underline"
                >
                  Forgot Password?
                </button>
              </div>

              <Button
                type="submit"
                className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg"
                disabled={isLoading}
              >
                {isLoading ? 'Logging In...' : 'Login'}
              </Button>

              <div className="text-center space-y-2">
                <p className="text-sm text-gray-600">
                  {"Don't have an account? "}
                  <Link href="/auth/signup" className="text-[#00B2FF] bg-blue-50 px-3 py-1 rounded-full text-sm hover:bg-blue-100">
                    Register Now
                  </Link>
                </p>
                <div className="flex items-center gap-2 justify-center">
                  <p className="text-sm text-gray-600">Part of a Household?</p>
                  <Link
                    href="/auth/household-login"
                    className="text-[#00B2FF] bg-blue-50 px-3 py-1 rounded-full text-sm hover:bg-blue-100"
                  >
                    Click Here
                  </Link>
                </div>
              </div>
            </form>
          ) : (
            <form onSubmit={handleResetPassword} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">OTP</label>
                <Input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  placeholder="Enter the OTP"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">New Password</label>
                <Input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter your new password"
                  required
                />
              </div>

              <Button
                type="submit"
                className="w-full bg-[#FF9500] hover:bg-[#FF9500]/90 py-6 text-lg"
                disabled={isLoading}
              >
                {isLoading ? 'Resetting Password...' : 'Reset Password'}
              </Button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}