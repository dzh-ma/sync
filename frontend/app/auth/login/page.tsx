// login/page.tsx
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
import { useUser } from "@/contexts/UserContext"; // Import the user context

// API base URL with fallback
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useUser(); // Use the login function from context
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [isLoading, setIsLoading] = useState(false);
  const [isForgotPassword, setIsForgotPassword] = useState(false);
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [verificationEmail, setVerificationEmail] = useState("");

  // Handle login form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate inputs
    if (!formData.email || !formData.password) {
      toast({
        title: "Missing Information",
        description: "Please enter both email and password",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      // Using the correct API endpoint format from the documentation
      const response = await axios.post(`${API_URL}/users/`, 
        new URLSearchParams({
          'username': formData.email, // The API expects 'username' for email
          'password': formData.password
        }), 
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      );

      // Extract token and store it
      const { access_token, token_type } = response.data;
      
      // Use the login function from context to update global state
      login({
        email: formData.email,
        isAuthenticated: true,
        token: access_token
      });

      toast({
        title: "Login Successful",
        description: "Welcome back!",
        variant: "default",
      });
      
      // Redirect to dashboard
      router.push("/dashboard");
    } catch (error) {
      // Handle common error scenarios
      console.error("Login error:", error);
      
      const errorMessage =
        (error as any).response?.data?.detail ||
        (error as any).message ||
        "Authentication failed. Please check your credentials and try again.";
      
      toast({
        title: "Login Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle forgot password request
  const handleForgotPassword = async () => {
    if (!formData.email) {
      toast({
        title: "Email Required",
        description: "Please enter your email address",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      // Store the email for the verification step
      setVerificationEmail(formData.email);
      
      // Request password reset
      await axios.post(`${API_URL}/users/request-password-reset`, { 
        email: formData.email 
      });
      
      toast({
        title: "Verification Email Sent",
        description: "A confirmation link has been sent to your email",
        variant: "default",
      });
      
      setIsForgotPassword(true);
    } catch (error) {
      const errorMessage =
        (error as any).response?.data?.detail ||
        (error as any).message ||
        "Failed to process your request. The email may not be registered.";
      
      toast({
        title: "Request Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle password reset
  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!otp || !newPassword) {
      toast({
        title: "Missing Information",
        description: "Please enter both the verification code and new password",
        variant: "destructive",
      });
      return;
    }

    // Validate password
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{}|;':",.<>?/])[A-Za-z\d!@#$%^&*()_+\-=\[\]{}|;':",.<>?/]{8,}$/;
    if (!passwordRegex.test(newPassword)) {
      toast({
        title: "Invalid Password",
        description: "Password must be at least 8 characters with uppercase, lowercase, numbers, and special characters.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);

    try {
      // Verify the OTP
      await axios.post(`${API_URL}/users/verify-reset-code`, { 
        email: verificationEmail || formData.email, 
        code: otp 
      });
      
      // Update the password
      await axios.post(`${API_URL}/users/reset-password`, { 
        email: verificationEmail || formData.email, 
        new_password: newPassword 
      });
      
      toast({
        title: "Password Reset Successful",
        description: "Your password has been updated. You can now log in with your new password.",
        variant: "default",
      });
      
      // Reset form state
      setIsForgotPassword(false);
      setOtp("");
      setNewPassword("");
      setFormData({ ...formData, password: "" });
    } catch (error) {
      const errorMessage =
        (error as any).response?.data?.detail ||
        (error as any).message ||
        "Failed to reset password. Please try again or request a new code.";
      
      toast({
        title: "Reset Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      <div className="hidden lg:flex lg:flex-1 relative">
        <Image
          src="https://media.istockphoto.com/id/1219569858/photo/woman-cooking-on-the-modern-kitchen-at-home.jpg?s=612x612&w=0&k=20&c=oUTIUAb0_cALWZ2GCTI3ZUmZCH31cf0UmBMPf1tMsck="
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
            <p className="text-gray-600">Smart Home Login</p>
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
                <label className="text-sm font-medium">Verification Code</label>
                <Input
                  type="text"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  placeholder="Enter the verification code"
                  required
                />
                <p className="text-xs text-gray-500">
                  Enter the code sent to your email
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">New Password</label>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Enter your new password"
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
                <p className="text-xs text-gray-500">
                  Password must be at least 8 characters with letters, numbers, and special characters.
                </p>
              </div>

              <div className="flex space-x-2">
                <Button
                  type="button"
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800"
                  onClick={() => setIsForgotPassword(false)}
                >
                  Back to Login
                </Button>
                <Button
                  type="submit"
                  className="flex-1 bg-[#FF9500] hover:bg-[#FF9500]/90"
                  disabled={isLoading}
                >
                  {isLoading ? 'Resetting...' : 'Reset Password'}
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
