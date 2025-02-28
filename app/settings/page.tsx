"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { motion } from "framer-motion";
import {
  Bell,
  Moon,
  Sun,
  Shield,
  Wifi,
  Volume2,
  BellRing,
  Globe,
  HardDrive,
  RefreshCw,
  Smartphone,
  Zap,
  Settings2,
} from "lucide-react";
import { NavigationSidebar } from "@/app/components/navigation-sidebar"; // Import the navbar

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

export default function SettingsPage() {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [sound, setSound] = useState(true);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex">
      <NavigationSidebar />
      <div className="flex-1 ml-[72px]">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="p-6"
        >
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
            <header className="flex justify-between items-center mb-8">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                  <Settings2 className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-800">Settings</h1>
                  <p className="text-sm text-gray-500">Customize your smart home experience</p>
                </div>
              </div>
            </header>
          </motion.div>

          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="grid grid-cols-1 md:grid-cols-2 gap-6"
          >
            <motion.div variants={item}>
              <Card className="overflow-hidden border-t-4 border-t-[#00B2FF]">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-[#00B2FF]">
                    <Zap className="h-5 w-5" />
                    General Settings
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <div className="flex items-center gap-3">
                      <Bell className="h-5 w-5 text-[#00B2FF]" />
                      <div>
                        <p className="font-medium">Notifications</p>
                        <p className="text-sm text-gray-500">Enable push notifications</p>
                      </div>
                    </div>
                    <Switch
                      checked={notifications}
                      onCheckedChange={setNotifications}
                      className="data-[state=checked]:bg-[#00B2FF]"
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <div className="flex items-center gap-3">
                      <Moon className="h-5 w-5 text-[#00B2FF]" />
                      <div>
                        <p className="font-medium">Dark Mode</p>
                        <p className="text-sm text-gray-500">Toggle dark mode theme</p>
                      </div>
                    </div>
                    <Switch
                      checked={darkMode}
                      onCheckedChange={setDarkMode}
                      className="data-[state=checked]:bg-[#00B2FF]"
                    />
                  </div>

                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <div className="flex items-center gap-3">
                      <Volume2 className="h-5 w-5 text-[#00B2FF]" />
                      <div>
                        <p className="font-medium">Sound Effects</p>
                        <p className="text-sm text-gray-500">Enable sound effects</p>
                      </div>
                    </div>
                    <Switch checked={sound} onCheckedChange={setSound} className="data-[state=checked]:bg-[#00B2FF]" />
                  </div>

                  <div className="space-y-2 p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <div className="flex items-center gap-3 mb-3">
                      <Globe className="h-5 w-5 text-[#00B2FF]" />
                      <Label className="font-medium">Language</Label>
                    </div>
                    <Select defaultValue="en">
                      <SelectTrigger className="w-full border-[#00B2FF] focus:ring-[#00B2FF]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="es">Spanish</SelectItem>
                        <SelectItem value="fr">French</SelectItem>
                        <SelectItem value="de">German</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={item}>
              <Card className="overflow-hidden border-t-4 border-t-[#FF9500]">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-[#FF9500]">
                    <Shield className="h-5 w-5" />
                    Network & Security
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2 p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <div className="flex items-center gap-3 mb-3">
                      <Wifi className="h-5 w-5 text-[#FF9500]" />
                      <Label className="font-medium">WiFi Network</Label>
                    </div>
                    <div className="flex gap-2">
                      <Input
                        value="MyHomeNetwork"
                        readOnly
                        className="flex-1 border-[#FF9500] focus-visible:ring-[#FF9500]"
                      />
                      <Button
                        variant="outline"
                        size="icon"
                        className="text-[#FF9500] border-[#FF9500] hover:bg-[#FF9500] hover:text-white"
                      >
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="space-y-2 p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <div className="flex items-center gap-3 mb-3">
                      <Shield className="h-5 w-5 text-[#FF9500]" />
                      <Label className="font-medium">Security Level</Label>
                    </div>
                    <Select defaultValue="high">
                      <SelectTrigger className="w-full border-[#FF9500] focus:ring-[#FF9500]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="high">High Security</SelectItem>
                        <SelectItem value="medium">Medium Security</SelectItem>
                        <SelectItem value="low">Low Security</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2 p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <div className="flex items-center gap-3 mb-3">
                      <HardDrive className="h-5 w-5 text-[#FF9500]" />
                      <Label className="font-medium">Backup Frequency</Label>
                    </div>
                    <Select defaultValue="daily">
                      <SelectTrigger className="w-full border-[#FF9500] focus:ring-[#FF9500]">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="daily">Daily</SelectItem>
                        <SelectItem value="weekly">Weekly</SelectItem>
                        <SelectItem value="monthly">Monthly</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={item}>
              <Card className="overflow-hidden border-t-4 border-t-[#00B2FF]">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-[#00B2FF]">
                    <BellRing className="h-5 w-5" />
                    Notification Preferences
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <div className="flex items-center gap-3">
                      <BellRing className="h-5 w-5 text-[#00B2FF]" />
                      <span className="font-medium">Device Alerts</span>
                    </div>
                    <Switch defaultChecked className="data-[state=checked]:bg-[#00B2FF]" />
                  </div>

                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <div className="flex items-center gap-3">
                      <Shield className="h-5 w-5 text-[#00B2FF]" />
                      <span className="font-medium">Security Alerts</span>
                    </div>
                    <Switch defaultChecked className="data-[state=checked]:bg-[#00B2FF]" />
                  </div>

                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <div className="flex items-center gap-3">
                      <Sun className="h-5 w-5 text-[#00B2FF]" />
                      <span className="font-medium">Energy Reports</span>
                    </div>
                    <Switch defaultChecked className="data-[state=checked]:bg-[#00B2FF]" />
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div variants={item}>
              <Card className="overflow-hidden border-t-4 border-t-[#FF9500]">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-[#FF9500]">
                    <Smartphone className="h-5 w-5" />
                    System Information
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <Label className="text-sm text-gray-500">System Version</Label>
                    <p className="font-medium text-[#FF9500]">2.1.0</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <Label className="text-sm text-gray-500">Last Updated</Label>
                    <p className="font-medium text-[#FF9500]">January 15, 2024</p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg transition-colors hover:bg-gray-100">
                    <Label className="text-sm text-gray-500">Device ID</Label>
                    <p className="font-medium text-[#FF9500]">SYNC-HUB-001234</p>
                  </div>

                  <Button
                    variant="outline"
                    className="w-full h-12 mt-4 border-[#FF9500] text-[#FF9500] hover:bg-[#FF9500] hover:text-white transition-colors"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Check for Updates
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}