"use client";

import React from "react";

import { useState, useEffect } from "react";
import { Card, CardContent } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../../components/ui/dialog";
import { useLogout } from "../../components/logout";
import { motion } from "framer-motion";
import { User, Settings, BarChart2, Users, LogOut, Plus, Lock } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Link from "next/link";
import { toast } from "../../components/ui/use-toast";
import Image from "next/image";
import { NavigationSidebar } from "../../components/navigation-sidebar"; // Import the navbar

interface FamilyMember {
  id: string;
  name: string;
  email: string;
  role: string;
}

export default function ProfilePage() {
  const [isEditProfileOpen, setIsEditProfileOpen] = useState(false);
  const [editProfileData, setEditProfileData] = useState({
    name: "",
    email: "",
  });
  const [user, setUser] = useState<any>(null);
  const logout = useLogout();
  const navigate = useNavigate();

  useEffect(() => {
    const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
    if (!currentUser.id) {
      navigate("/auth/login");
      return;
    }
    setUser(currentUser);
    setEditProfileData({
      name: currentUser.name,
      email: currentUser.email,
    });
  }, [navigate]);

  const handleEditProfile = () => {
    // In a real application, this would update the user's information in the backend
    setUser({ ...user, ...editProfileData });
    localStorage.setItem("currentUser", JSON.stringify({ ...user, ...editProfileData }));
    setIsEditProfileOpen(false);
    toast({
      title: "Profile Updated",
      description: "Your profile information has been updated successfully.",
    });
  };

  const handleRequestAccess = (feature: string) => {
    // In a real application, this would send a request to the admin
    toast({
      title: "Access Requested",
      description: `Your request for access to ${feature} has been sent to the admin.`,
    });
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <NavigationSidebar />
      <div className="flex-1 ml-[72px]">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="p-6"
        >
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <Card className="max-w-4xl mx-auto">
              <CardContent className="p-6">
                <div className="flex justify-between items-start mb-8">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                      <User className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold text-gray-800">Profile</h1>
                      <p className="text-sm text-gray-500">Manage your account and family members</p>
                    </div>
                  </div>
                  <Button variant="outline" className="text-[#00B2FF]" onClick={() => setIsEditProfileOpen(true)}>
                    <Settings className="w-4 h-4 mr-2" />
                    Edit Profile
                  </Button>
                </div>

                <div className="flex flex-col md:flex-row items-center mb-8 bg-white p-6 rounded-lg shadow-sm">
                  <div className="relative w-32 h-32 mb-4 md:mb-0 md:mr-6">
                    <Image src="/placeholder.svg" alt="Profile" layout="fill" className="rounded-full object-cover" />
                  </div>
                  <div className="text-center md:text-left">
                    <h3 className="text-2xl font-semibold mb-1">{user.name}</h3>
                    <p className="text-gray-600 mb-1">{user.email}</p>
                    <p className="text-[#00B2FF] font-medium">{user.role}</p>
                    <div className="flex gap-2 mt-4">
                      <Button className="bg-[#00B2FF] hover:bg-[#00B2FF]/90" onClick={() => setIsEditProfileOpen(true)}>
                        Edit Profile
                      </Button>
                      <Button variant="outline" onClick={logout}>
                        <LogOut className="w-4 h-4 mr-2" />
                        Logout
                      </Button>
                    </div>
                  </div>
                </div>

                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="grid grid-cols-1 md:grid-cols-2 gap-4"
                >
                  {user.type === "admin" ? (
                    <>
                      <Link href="/create-profile">
                        <Button className="w-full h-12 bg-[#00B2FF] text-white hover:bg-[#00B2FF]/90">
                          <Plus className="w-4 h-4 mr-2" />
                          Create Profile
                        </Button>
                      </Link>

                      <Link href="/manage-profiles">
                        <Button
                          variant="outline"
                          className="w-full h-12 text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF]/10"
                        >
                          <Users className="w-4 h-4 mr-2" />
                          Manage Profiles
                        </Button>
                      </Link>

                      <Button
                        variant="outline"
                        className="w-full h-12 text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF]/10"
                        onClick={() => navigate("/statistics")}
                      >
                        <BarChart2 className="w-4 h-4 mr-2" />
                        View Analytics
                      </Button>

                      <Button
                        variant="outline"
                        className="w-full h-12 text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF]/10"
                        onClick={() => navigate("/settings")}
                      >
                        <Settings className="w-4 h-4 mr-2" />
                        Account Settings
                      </Button>
                    </>
                  ) : (
                    <>
                      {!user.permissions?.analyticalData && (
                        <Button
                          variant="outline"
                          className="w-full h-12 text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF]/10"
                          onClick={() => handleRequestAccess("Analytical Data")}
                        >
                          <Lock className="w-4 h-4 mr-2" />
                          Request Analytics Access
                        </Button>
                      )}
                      {!user.permissions?.addAutomation && (
                        <Button
                          variant="outline"
                          className="w-full h-12 text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF]/10"
                          onClick={() => handleRequestAccess("Automation")}
                        >
                          <Lock className="w-4 h-4 mr-2" />
                          Request Automation Access
                        </Button>
                      )}
                      <Button
                        variant="outline"
                        className="w-full h-12 text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF]/10"
                        onClick={() => navigate("/settings")}
                      >
                        <Settings className="w-4 h-4 mr-2" />
                        Account Settings
                      </Button>
                    </>
                  )}
                </motion.div>
              </CardContent>
            </Card>
          </motion.div>

          <Dialog open={isEditProfileOpen} onOpenChange={setIsEditProfileOpen}>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Edit Profile</DialogTitle>
                <DialogDescription>Make changes to your profile here.</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="edit-name" className="text-right">
                    Name
                  </Label>
                  <Input
                    id="edit-name"
                    value={editProfileData.name}
                    onChange={(e) => setEditProfileData({ ...editProfileData, name: e.target.value })}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="edit-email" className="text-right">
                    Email
                  </Label>
                  <Input
                    id="edit-email"
                    type="email"
                    value={editProfileData.email}
                    onChange={(e) => setEditProfileData({ ...editProfileData, email: e.target.value })}
                    className="col-span-3"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" onClick={handleEditProfile}>
                  Save changes
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </motion.div>
      </div>
    </div>
  );
}
