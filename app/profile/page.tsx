"use client";

import type React from "react";
import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useLogout } from "@/app/components/logout";
import { motion } from "framer-motion";
import { User, Settings, BarChart2, Users, LogOut, Plus, Lock } from "lucide-react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast } from "@/components/ui/use-toast";
import Image from "next/image";
import { NavigationSidebar } from "@/app/components/navigation-sidebar";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const AVATAR_OPTIONS = {
  male: ["/avatar1.jpg", "/avatar2.jpg", "/avatar3.png"],
  female: ["/avatar4.jpg", "/avatar5.jpg", "/avatar6.jpg"],
};

interface FamilyMember {
  id: string;
  name: string;
  email: string;
  role: string;
}

export default function ProfilePage() {
  const [isEditProfileOpen, setIsEditProfileOpen] = useState(false);
  const [isAvatarSelectOpen, setIsAvatarSelectOpen] = useState(false);
  const [editProfileData, setEditProfileData] = useState({
    name: "",
    email: "",
    avatar: "",
  });
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const logout = useLogout();
  const router = useRouter();

  // Fetch user data
  useEffect(() => {
    const fetchUserData = async () => {
      setIsLoading(true);
      try {
        // Check if we have a user in localStorage
        const storedUser = localStorage.getItem("currentUser");
        const storedMember = localStorage.getItem("currentMember");
        
        if (!storedUser && !storedMember) {
          router.push("/auth/login");
          return;
        }
        
        // Initialize with localStorage data first
        let userData = null;
        
        if (storedUser) {
          // Admin user
          const currentUser = JSON.parse(storedUser);
          userData = currentUser;
          
          if (currentUser.id) {
            try {
              // Fetch the latest data from the backend
              const response = await fetch(`${API_URL}/api/user/${currentUser.id}`);
              
              if (response.ok) {
                const apiData = await response.json();
                
                // Format the user data
                userData = {
                  id: apiData._id,
                  type: "admin",
                  email: apiData.admin_email,
                  name: `${apiData.firstName || ""} ${apiData.lastName || ""}`.trim() || "Admin",
                  role: "Admin",
                  householdId: apiData.household_id,
                  avatar: apiData.avatar,
                };
                
                // Update localStorage with fresh data
                localStorage.setItem("currentUser", JSON.stringify(userData));
              }
            } catch (error) {
              console.error("Error fetching user data from API:", error);
              // Continue with localStorage data
            }
          }
        } else if (storedMember) {
          // Household member
          const currentMember = JSON.parse(storedMember);
          userData = currentMember;
          
          if (currentMember.email) {
            try {
              // Fetch the latest data from the backend
              const response = await fetch(`${API_URL}/api/household-member/${currentMember.email}`);
              
              if (response.ok) {
                const apiData = await response.json();
                
                // Format the member data
                userData = {
                  id: apiData._id,
                  type: "member",
                  email: apiData.email,
                  name: apiData.name,
                  role: apiData.role || "Family Member",
                  householdId: apiData.household_id,
                  avatar: apiData.avatar,
                  accountType: apiData.account_type,
                  permissions: apiData.permissions,
                };
                
                // Update localStorage with fresh data
                localStorage.setItem("currentMember", JSON.stringify(userData));
              }
            } catch (error) {
              console.error("Error fetching member data from API:", error);
              // Continue with localStorage data
            }
          }
        }
        
        if (userData) {
          setUser(userData);
          setEditProfileData({
            name: userData.name || "",
            email: userData.email || "",
            avatar: userData.avatar || "",
          });
        } else {
          router.push("/auth/login");
        }
      } catch (error) {
        console.error("Error loading user data:", error);
        toast({
          title: "Error",
          description: "Failed to load profile data",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchUserData();
  }, [router]);

  const handleEditProfile = async () => {
    try {
      if (!user) return;
      
      const updatedUserData = {
        ...user,
        name: editProfileData.name,
        email: editProfileData.email,
        avatar: editProfileData.avatar,
      };
      
      if (user.type === "admin") {
        // Parse name into first and last name
        const nameParts = editProfileData.name.split(" ");
        const firstName = nameParts[0] || "";
        const lastName = nameParts.slice(1).join(" ") || "";
        
        // Call API to update admin profile
        const response = await fetch(`${API_URL}/api/update-admin-profile`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: editProfileData.email,
            firstName,
            lastName,
            avatar: editProfileData.avatar,
          }),
        });
        
        if (!response.ok) {
          throw new Error("Failed to update profile");
        }
        
        // Update localStorage
        localStorage.setItem("currentUser", JSON.stringify(updatedUserData));
      } else {
        // Call API to update household member
        const response = await fetch(`${API_URL}/api/update-household-member/${user.email}`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: editProfileData.name,
            email: editProfileData.email,
            role: user.role,
            avatar: editProfileData.avatar,
          }),
        });
        
        if (!response.ok) {
          throw new Error("Failed to update profile");
        }
        
        // Update localStorage
        localStorage.setItem("currentMember", JSON.stringify(updatedUserData));
      }
      
      // Update local state
      setUser(updatedUserData);
      setIsEditProfileOpen(false);
      
      toast({
        title: "Success",
        description: "Profile updated successfully",
      });
    } catch (error) {
      console.error("Error updating profile:", error);
      toast({
        title: "Error",
        description: "Failed to update profile",
        variant: "destructive",
      });
    }
  };

  const handleAvatarSelect = (avatar: string) => {
    setEditProfileData({ ...editProfileData, avatar });
    setIsAvatarSelectOpen(false);
  };

  const handleRequestAccess = (feature: string) => {
    toast({
      title: "Access Requested",
      description: `Your request for access to ${feature} has been sent to the admin.`,
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-t-4 border-[#00B2FF] border-solid rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <NavigationSidebar />
      <div className="max-w-6xl mx-auto px-4 py-8 ml-[92px]">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: [0.25, 0.25, 0, 1], staggerChildren: 0.1 }}
        >
          <div className="flex justify-between items-center mb-10">
            <div className="flex items-center space-x-4">
              <div className="w-14 h-14 bg-[#00B2FF] rounded-full flex items-center justify-center text-white">
                {user.avatar ? (
                  <Image
                    src={user.avatar}
                    alt="User avatar"
                    width={56}
                    height={56}
                    className="rounded-full object-cover"
                  />
                ) : (
                  <User size={28} />
                )}
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">Profile Dashboard</h1>
                <p className="text-gray-500">Manage your account and family members</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md border border-gray-100 p-8 mb-10">
            <div className="flex flex-col md:flex-row md:items-center gap-6">
              <div className="w-24 h-24 bg-[#00B2FF]/10 rounded-full flex items-center justify-center mx-auto md:mx-0">
                {user.avatar ? (
                  <Image
                    src={user.avatar}
                    alt="User avatar"
                    width={96}
                    height={96}
                    className="rounded-full object-cover"
                  />
                ) : (
                  <User size={40} className="text-[#00B2FF]" />
                )}
              </div>
              <div className="flex-1 text-center md:text-left">
                <h2 className="text-2xl font-bold text-gray-800 mb-1">{user.name}</h2>
                <p className="text-gray-500 mb-4">{user.email}</p>
                <div className="flex flex-wrap gap-3 justify-center md:justify-start">
                  <button
                    onClick={() => setIsEditProfileOpen(true)}
                    className="px-5 py-2.5 bg-[#00B2FF] text-white rounded-lg hover:bg-[#00B2FF]/90 transition-all shadow-sm"
                  >
                    Edit Profile
                  </button>
                  <button
                    onClick={logout}
                    className="flex items-center space-x-2 px-5 py-2.5 bg-white border border-gray-200 rounded-lg text-[#0B0B0B] hover:bg-gray-50 transition-all shadow-sm"
                  >
                    <LogOut size={18} />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          {user.type === "admin" && (
            <>
              <h3 className="text-xl font-semibold text-gray-800 mb-6">Quick Actions</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
                <Link href="/create-profile" className="block">
                  <button className="w-full bg-white rounded-xl shadow-md border border-gray-100 p-6 hover:shadow-lg transition-all group">
                    <div className="flex items-center space-x-4">
                      <div className="w-14 h-14 bg-[#00B2FF]/10 rounded-full flex items-center justify-center text-[#00B2FF] group-hover:scale-110 transition-all duration-300">
                        <Plus size={28} />
                      </div>
                      <div className="text-left">
                        <h3 className="text-lg font-semibold text-gray-800">Create Profile</h3>
                        <p className="text-gray-500">Add a new user or family member</p>
                      </div>
                    </div>
                  </button>
                </Link>
                <Link href="/manage-profiles" className="block">
                  <button className="w-full bg-white rounded-xl shadow-md border border-gray-100 p-6 hover:shadow-lg transition-all group">
                    <div className="flex items-center space-x-4">
                      <div className="w-14 h-14 bg-[#00B2FF]/10 rounded-full flex items-center justify-center text-[#00B2FF] group-hover:scale-110 transition-all duration-300">
                        <Users size={28} />
                      </div>
                      <div className="text-left">
                        <h3 className="text-lg font-semibold text-gray-800">Manage Profiles</h3>
                        <p className="text-gray-500">View and edit existing profiles</p>
                      </div>
                    </div>
                  </button>
                </Link>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-6">Account Management</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <button
                  onClick={() => router.push("/statistics")}
                  className="bg-white rounded-xl shadow-md border border-gray-100 p-6 hover:shadow-lg transition-all group"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-14 h-14 bg-[#00B2FF]/10 rounded-full flex items-center justify-center text-[#00B2FF] group-hover:text-[#00B2FF] transition-all">
                      <BarChart2 size={28} />
                    </div>
                    <div className="text-left">
                      <h3 className="text-lg font-semibold text-gray-800">View Analytics</h3>
                      <p className="text-gray-500">Check usage statistics and reports</p>
                    </div>
                  </div>
                </button>
                <button
                  onClick={() => router.push("/settings")}
                  className="bg-white rounded-xl shadow-md border border-gray-100 p-6 hover:shadow-lg transition-all group"
                >
                  <div className="flex items-center space-x-4">
                    <div className="w-14 h-14 bg-[#00B2FF]/10 rounded-full flex items-center justify-center text-[#00B2FF] group-hover:text-[#00B2FF] transition-all">
                      <Settings size={28} />
                    </div>
                    <div className="text-left">
                      <h3 className="text-lg font-semibold text-gray-800">Account Settings</h3>
                      <p className="text-gray-500">Manage preferences and security</p>
                    </div>
                  </div>
                </button>
              </div>
            </>
          )}

          {user.type === "member" && (
            <>
              <h3 className="text-xl font-semibold text-gray-800 mb-6">Account Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
                <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className="w-10 h-10 bg-[#00B2FF]/10 rounded-full flex items-center justify-center text-[#00B2FF]">
                      <User size={20} />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">Account Type</h3>
                      <p className="text-gray-500">{user.accountType || "Family Member"}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-[#00B2FF]/10 rounded-full flex items-center justify-center text-[#00B2FF]">
                      <Lock size={20} />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">Permissions</h3>
                      <p className="text-gray-500">
                        {user.permissions
                          ? Object.keys(user.permissions).filter(
                              (key) => user.permissions[key]
                            ).length + " permissions enabled"
                          : "Basic access"}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="bg-white rounded-xl shadow-md border border-gray-100 p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Need More Access?</h3>
                  <p className="text-gray-500 mb-4">Request additional permissions from your admin</p>
                  <div className="space-y-2">
                    {!user.permissions?.deviceControl && (
                      <button
                        onClick={() => handleRequestAccess("Device Control")}
                        className="w-full px-4 py-2 bg-[#00B2FF]/10 text-[#00B2FF] rounded hover:bg-[#00B2FF]/20 transition-colors text-sm font-medium"
                      >
                        Request Device Control
                      </button>
                    )}
                    {!user.permissions?.roomAccess && (
                      <button
                        onClick={() => handleRequestAccess("Room Management")}
                        className="w-full px-4 py-2 bg-[#00B2FF]/10 text-[#00B2FF] rounded hover:bg-[#00B2FF]/20 transition-colors text-sm font-medium"
                      >
                        Request Room Management
                      </button>
                    )}
                    {!user.permissions?.automationAccess && (
                      <button
                        onClick={() => handleRequestAccess("Automation Access")}
                        className="w-full px-4 py-2 bg-[#00B2FF]/10 text-[#00B2FF] rounded hover:bg-[#00B2FF]/20 transition-colors text-sm font-medium"
                      >
                        Request Automation Access
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </>
          )}
        </motion.div>
      </div>

      {/* Edit Profile Dialog */}
      <Dialog open={isEditProfileOpen} onOpenChange={setIsEditProfileOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Edit Profile</DialogTitle>
            <DialogDescription>
              Make changes to your profile information here. Click save when you're done.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="flex flex-col items-center space-y-4 mb-4">
              <div
                className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center cursor-pointer relative overflow-hidden"
                onClick={() => setIsAvatarSelectOpen(true)}
              >
                {editProfileData.avatar ? (
                  <Image
                    src={editProfileData.avatar}
                    alt="Avatar"
                    fill
                    className="object-cover"
                  />
                ) : (
                  <User size={40} className="text-gray-400" />
                )}
                <div className="absolute inset-0 bg-black/30 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                  <span className="text-white text-xs font-medium">Change</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setIsAvatarSelectOpen(true)}
                className="text-sm text-blue-600 hover:underline"
              >
                Change Avatar
              </button>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                Name
              </Label>
              <Input
                id="name"
                value={editProfileData.name}
                onChange={(e) => setEditProfileData({ ...editProfileData, name: e.target.value })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="email" className="text-right">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                value={editProfileData.email}
                onChange={(e) => setEditProfileData({ ...editProfileData, email: e.target.value })}
                className="col-span-3"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditProfileOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEditProfile}>Save changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Avatar Select Dialog */}
      <Dialog open={isAvatarSelectOpen} onOpenChange={setIsAvatarSelectOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Select Avatar</DialogTitle>
            <DialogDescription>Choose an avatar for your profile</DialogDescription>
          </DialogHeader>
          <div className="grid grid-cols-3 gap-4 py-4">
            {AVATAR_OPTIONS.male.map((avatar, index) => (
              <div
                key={`male-${index}`}
                className="relative w-24 h-24 cursor-pointer mx-auto"
                onClick={() => handleAvatarSelect(avatar)}
              >
                <Image
                  src={avatar}
                  alt={`Male avatar ${index + 1}`}
                  fill
                  className="object-cover rounded-full"
                />
              </div>
            ))}
            {AVATAR_OPTIONS.female.map((avatar, index) => (
              <div
                key={`female-${index}`}
                className="relative w-24 h-24 cursor-pointer mx-auto"
                onClick={() => handleAvatarSelect(avatar)}
              >
                <Image
                  src={avatar}
                  alt={`Female avatar ${index + 1}`}
                  fill
                  className="object-cover rounded-full"
                />
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAvatarSelectOpen(false)}>
              Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}