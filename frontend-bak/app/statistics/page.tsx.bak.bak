"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LineChart, BarChart, PieChart } from "@/components/charts";
import { Download, User, BarChart2, PieChartIcon, TrendingUp, Lock, FileText } from "lucide-react";
import { PDFDocument, rgb } from "pdf-lib";
import { toPng } from "html-to-image";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ui/use-toast";
import { NavigationSidebar } from "@/app/components/navigation-sidebar"; // Import the navbar
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import generateEnhancedReport from "@/components/generate-enhanced-reports";

interface Device {
  id: string;
  name: string;
  type: string;
  room: string;
  status: "on" | "off";
  powerConsumption: number;
  lastStatusChange: number;
  totalEnergyConsumed: number;
}

interface Room {
  id: string;
  name: string;
}

// Original PDF generation function (kept for backward compatibility)
const generatePDF = async (devices: Device[], rooms: Room[]) => {
  const pdfDoc = await PDFDocument.create();
  const page = pdfDoc.addPage();
  const { width, height } = page.getSize();
  const fontSize = 12;

  // Add title
  page.drawText("Energy Consumption Report", {
    x: 50,
    y: height - 50,
    size: 20,
    color: rgb(0, 0, 0),
  });

  // Add date
  const currentDate = new Date().toLocaleDateString();
  page.drawText(`Generated on: ${currentDate}`, {
    x: 50,
    y: height - 80,
    size: fontSize,
    color: rgb(0.5, 0.5, 0.5),
  });

  // Add device usage table
  page.drawText("Device Usage", {
    x: 50,
    y: height - 120,
    size: 16,
    color: rgb(0, 0, 0),
  });

  devices.forEach((device, index) => {
    page.drawText(`${device.name} (${device.type}): ${device.totalEnergyConsumed.toFixed(2)} kWh`, {
      x: 50,
      y: height - 150 - index * 20,
      size: fontSize,
      color: rgb(0, 0, 0),
    });
  });

  // Add room usage table
  page.drawText("Room Usage", {
    x: 50,
    y: height - 300,
    size: 16,
    color: rgb(0, 0, 0),
  });

  rooms.forEach((room, index) => {
    const roomUsage = devices.filter((d) => d.room === room.name).reduce((sum, d) => sum + d.totalEnergyConsumed, 0);
    page.drawText(`${room.name}: ${roomUsage.toFixed(2)} kWh`, {
      x: 50,
      y: height - 330 - index * 20,
      size: fontSize,
      color: rgb(0, 0, 0),
    });
  });

  // Add charts
  const charts = document.querySelectorAll(".chart-container");
  for (let i = 0; i < charts.length; i++) {
    const chart = charts[i] as HTMLElement;

    // Add a style tag with the necessary font information
    const style = document.createElement("style");
    chart.prepend(style);

    const pngImage = await toPng(chart, {
      quality: 0.95,
      backgroundColor: "#ffffff",
      style: {
        // Add any additional styles here if needed
      },
    });

    // Remove the added style tag
    chart.removeChild(style);

    const image = await pdfDoc.embedPng(pngImage);

    page.drawImage(image, {
      x: 50,
      y: height - 500 - i * 300,
      width: 500,
      height: 250,
    });
  }

  const pdfBytes = await pdfDoc.save();
  const blob = new Blob([pdfBytes], { type: "application/pdf" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "energy_statistics.pdf";
  link.click();
};

// New function to download enhanced reports from the backend
const downloadEnhancedReport = async (format: string, timeRange: string, toast: any) => {
  try {
    // Convert time range to date range
    const endDate = new Date().toISOString().split('T')[0]; // Today in YYYY-MM-DD format
    let startDate;

    switch (timeRange) {
      case 'week':
        startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      break;
      case 'month':
        startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      break;
      case 'year':
        startDate = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      break;
      default: // day
        startDate = new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    }

    // Get auth token from local storage, handling potential parsing errors
    let token = "";
    try {
      // Try to get the user object
      const userStr = localStorage.getItem("currentUser");
      if (userStr) {
        const user = JSON.parse(userStr);
        token = user.token || localStorage.getItem("authToken") || "";
      } else {
        // If no user object, try a direct token
        token = localStorage.getItem("authToken") || "";
      }
    } catch (error) {
      console.error("Error parsing user data from localStorage:", error);
      // Try alternate token storage if the user object can't be parsed
      token = localStorage.getItem("authToken") || "";
    }

    if (!token) {
      toast({
        title: "Authentication Error",
        description: "You must be logged in to download reports.",
        variant: "destructive",
      });
      return;
    }

    // Call backend API
    // Check if the token already has "Bearer " prefix, if not add it
    const authToken = token.startsWith('Bearer ') ? token : `Bearer ${token}`;

    console.log(`Making request to backend with time range: ${timeRange} (${startDate} to ${endDate})`);

    const response = await fetch(`/api/v1/reports/report?format=${format}&start_date=${startDate}&end_date=${endDate}`, {
      method: 'POST',
      headers: {
        'Authorization': authToken,
        'Accept': 'application/octet-stream',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to download report");
    }

    // Handle the file download
    const blob = await response.blob();
    const fileExtension = format === 'pdf' ? 'pdf' : 'csv';
    const fileType = format === 'pdf' ? 'application/pdf' : 'text/csv';

    // Create a download link and trigger it
    const fileURL = URL.createObjectURL(new Blob([blob], { type: fileType }));
    const downloadLink = document.createElement('a');
    downloadLink.href = fileURL;
    downloadLink.download = `energy_report_${new Date().toISOString().split('T')[0]}.${fileExtension}`;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    toast({
      title: "Report Downloaded",
      description: `Your ${format.toUpperCase()} report has been downloaded successfully.`,
      variant: "default",
    });

  } catch (error) {
    console.error("Error downloading report:", error);
    toast({
      title: "Download Failed",
      description: error instanceof Error ? error.message : "Failed to download report. Please try again.",
      variant: "destructive",
    });
  }
};

export default function StatisticsPage() {
  const router = useRouter();
  const [devices, setDevices] = useState<Device[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [timeRange, setTimeRange] = useState("day");
  const [user, setUser] = useState<any>(null);
  const [isReportDialogOpen, setIsReportDialogOpen] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
    setUser(currentUser);

    const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]");
    const storedRooms = JSON.parse(localStorage.getItem("rooms") || "[]");
    setDevices(storedDevices);
    setRooms(storedRooms);
  }, [router]);

  const handleRequestAccess = () => {
    toast({
      title: "Access Requested",
      description: "Your request for access to Statistical Data has been sent to the admin.",
    });
  };

  const filterDataByTimeRange = (data: any[]) => {
    if (data.length === 0) return [];

    const now = new Date();
    const startDate = new Date();

    switch (timeRange) {
      case "week":
        startDate.setDate(now.getDate() - 7);
      break;
      case "month":
        startDate.setMonth(now.getMonth() - 1);
      break;
      case "year":
        startDate.setFullYear(now.getFullYear() - 1);
      break;
      default: // day
        startDate.setDate(now.getDate() - 1);
    }

    return data.filter((item: any) => new Date(item.lastStatusChange) >= startDate);
  };

  const calculateRoomUsage = (roomName: string): number => {
    return devices
    .filter((device) => device.room === roomName)
    .reduce((total, device) => total + device.totalEnergyConsumed, 0);
  };

  const deviceData =
    devices.length > 0
      ? filterDataByTimeRange(devices).map((device) => ({
        name: device.name,
        usage: Number.parseFloat(device.totalEnergyConsumed.toFixed(2)),
      }))
        : [];

        const roomData = rooms
        .map((room) => ({
          name: room.name,
          usage: Number.parseFloat(calculateRoomUsage(room.name).toFixed(2)),
        }))
        .filter((room) => room.usage > 0);

        const deviceTypeData =
          devices.length > 0
            ? filterDataByTimeRange(devices).reduce(
              (acc, device) => {
                acc[device.type] = (acc[device.type] || 0) + device.totalEnergyConsumed;
                return acc;
              },
              {} as Record<string, number>
            )
              : {};

              const totalEnergyConsumed = devices.reduce((total, device) => total + device.totalEnergyConsumed, 0);

              const containerVariants = {
                hidden: { opacity: 0 },
                visible: {
                  opacity: 1,
                  transition: {
                    staggerChildren: 0.1,
                  },
                },
              };

              const itemVariants = {
                hidden: { y: 20, opacity: 0 },
                visible: {
                  y: 0,
                  opacity: 1,
                },
              };

              if (!user) return null;

              if (user.type === "household" && !user.permissions?.statisticalData) {
                return (
                  <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                  <Card className="w-full max-w-md">
                  <CardContent className="flex flex-col items-center justify-center p-6">
                  <Lock className="w-12 h-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Access Required</h3>
                  <p className="text-sm text-gray-500 text-center mb-4">
                  You don't have permission to view statistical data.
                    </p>
                  <Button onClick={handleRequestAccess}>Request Access</Button>
                  </CardContent>
                  </Card>
                  </div>
                );
              }

              return (
                <div className="min-h-screen bg-gray-50 flex">
                <NavigationSidebar />
                <div className="flex-1 ml-[72px]">
                <motion.div
                initial="hidden"
                animate="visible"
                variants={containerVariants}
                className="p-6"
                >
                <motion.header variants={itemVariants} className="flex justify-between items-center mb-8">
                <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
                <BarChart2 className="h-6 w-6 text-white" />
                </div>
                <div>
                <h1 className="text-2xl font-bold text-gray-800">Energy Statistics</h1>
                <p className="text-sm text-gray-500">Monitor and analyze your energy consumption</p>
                </div>
                </div>
                <div className="flex items-center gap-4">
                <Select value={timeRange} onValueChange={setTimeRange}>
                <SelectTrigger className="w-[180px] border-[#00B2FF] text-[#00B2FF]">
                <SelectValue placeholder="Select time range" />
                </SelectTrigger>
                <SelectContent>
                <SelectItem value="day">Past 24 Hours</SelectItem>
                <SelectItem value="week">Past Week</SelectItem>
                <SelectItem value="month">Past Month</SelectItem>
                <SelectItem value="year">Past Year</SelectItem>
                </SelectContent>
                </Select>

                {/* Dialog for Enhanced Report Download */}
                <Dialog open={isReportDialogOpen} onOpenChange={setIsReportDialogOpen}>
                <DialogTrigger asChild>
                <Button
                variant="outline"
                size="icon"
                className="text-[#FF9500] border-[#FF9500] hover:bg-[#FF9500] hover:text-white"
                >
                <Download className="h-5 w-5" />
                </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-md">
                <DialogHeader>
                <DialogTitle>Download Energy Report</DialogTitle>
                <DialogDescription>
                Choose the format for your energy consumption report
                  </DialogDescription>
                </DialogHeader>
                <div className="grid grid-cols-2 gap-4 py-4">
                <Button
                onClick={() => {
                  downloadEnhancedReport('pdf', timeRange, toast);
                  setIsReportDialogOpen(false);
                }}
                className="flex flex-col items-center justify-center h-24 p-4 border rounded-lg hover:bg-blue-50"
                variant="outline"
                >
                <FileText className="h-8 w-8 mb-2 text-blue-600" />
                <span>PDF Report</span>
                <span className="text-xs text-gray-500">Rich visualizations</span>
                </Button>
                <Button
                onClick={() => {
                  downloadEnhancedReport('csv', timeRange, toast);
                  setIsReportDialogOpen(false);
                }}
                className="flex flex-col items-center justify-center h-24 p-4 border rounded-lg hover:bg-green-50"
                variant="outline"
                >
                <BarChart2 className="h-8 w-8 mb-2 text-green-600" />
                <span>CSV Data</span>
                <span className="text-xs text-gray-500">For data analysis</span>
                </Button>
                </div>
                <DialogFooter className="sm:justify-between">
                <Button
                variant="ghost"
                onClick={() => {
                  generatePDF(devices, rooms);
                  setIsReportDialogOpen(false);
                }}
                className="text-gray-500"
                >
                Use Legacy Report
                </Button>
                <DialogClose asChild>
                <Button type="button" variant="secondary">
                Cancel
                </Button>
                </DialogClose>
                </DialogFooter>
                </DialogContent>
                </Dialog>

                <Button
                variant="outline"
                size="icon"
                className="text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF] hover:text-white"
                >
                <User className="h-5 w-5" />
                </Button>
                </div>
                </motion.header>

                <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <motion.div variants={itemVariants}>
                <Card className="bg-gradient-to-br from-[#00B2FF] to-[#0085FF] text-white">
                <CardHeader>
                <CardTitle className="text-lg font-medium">Total Energy Consumed</CardTitle>
                </CardHeader>
                <CardContent>
                <div className="text-3xl font-bold">{totalEnergyConsumed.toFixed(2)} kWh</div>
                <p className="text-sm opacity-80">in the selected time range</p>
                </CardContent>
                </Card>
                </motion.div>
                <motion.div variants={itemVariants}>
                <Card className="bg-gradient-to-br from-[#FF9500] to-[#FFB800] text-white">
                <CardHeader>
                <CardTitle className="text-lg font-medium">Active Devices</CardTitle>
                </CardHeader>
                <CardContent>
                <div className="text-3xl font-bold">{devices.filter((d) => d.status === "on").length}</div>
                <p className="text-sm opacity-80">out of {devices.length} total devices</p>
                </CardContent>
                </Card>
                </motion.div>
                <motion.div variants={itemVariants}>
                <Card className="bg-gradient-to-br from-[#00B2FF] to-[#0085FF] text-white">
                <CardHeader>
                <CardTitle className="text-lg font-medium">Most Active Room</CardTitle>
                </CardHeader>
                <CardContent>
                <div className="text-3xl font-bold">
                {roomData.length > 0 ? roomData.reduce((a, b) => (a.usage > b.usage ? a : b)).name : "No data"}
                </div>
                <p className="text-sm opacity-80">based on energy consumption</p>
                </CardContent>
                </Card>
                </motion.div>
                </motion.div>

                <motion.div variants={itemVariants}>
                <Tabs defaultValue="devices" className="space-y-6">
                <TabsList className="bg-white shadow-md rounded-lg p-1">
                <TabsTrigger value="devices" className="data-[state=active]:bg-[#00B2FF] data-[state=active]:text-white">
                <BarChart2 className="h-4 w-4 mr-2" />
                Devices
                </TabsTrigger>
                <TabsTrigger value="rooms" className="data-[state=active]:bg-[#00B2FF] data-[state=active]:text-white">
                <PieChartIcon className="h-4 w-4 mr-2" />
                Rooms
                </TabsTrigger>
                <TabsTrigger value="overview" className="data-[state=active]:bg-[#00B2FF] data-[state=active]:text-white">
                <TrendingUp className="h-4 w-4 mr-2" />
                Overview
                </TabsTrigger>
                </TabsList>
                <TabsContent value="devices" className="space-y-6">
                <Card>
                <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800">Energy Usage by Device</CardTitle>
                </CardHeader>
                <CardContent>
                <div className="chart-container">
                {deviceData.length > 0 ? (
                  <BarChart data={deviceData} />
                ) : (
                <p className="text-center text-gray-500">No data available for the selected time range</p>
                )}
              </div>
              </CardContent>
              </Card>
              <Card>
              <CardHeader>
              <CardTitle className="text-xl font-semibold text-gray-800">Device Usage Over Time</CardTitle>
              </CardHeader>
              <CardContent>
              <div className="chart-container">
              {deviceData.length > 0 ? (
                <LineChart data={deviceData} />
              ) : (
              <p className="text-center text-gray-500">No data available for the selected time range</p>
              )}
            </div>
            </CardContent>
            </Card>
            </TabsContent>
            <TabsContent value="rooms" className="space-y-6">
            <Card>
            <CardHeader>
            <CardTitle className="text-xl font-semibold text-gray-800">Energy Usage by Room</CardTitle>
            </CardHeader>
            <CardContent>
            <div className="chart-container">
            {roomData.length > 0 ? (
              <BarChart data={roomData} />
            ) : (
            <p className="text-center text-gray-500">No data available for the selected time range</p>
            )}
          </div>
          </CardContent>
          </Card>
          <Card>
          <CardHeader>
          <CardTitle className="text-xl font-semibold text-gray-800">Room Usage Over Time</CardTitle>
          </CardHeader>
          <CardContent>
          <div className="chart-container">
          {roomData.length > 0 ? (
            <LineChart data={roomData} />
          ) : (
          <p className="text-center text-gray-500">No data available for the selected time range</p>
          )}
        </div>
        </CardContent>
        </Card>
        </TabsContent>
        <TabsContent value="overview" className="space-y-6">
        <Card>
        <CardHeader>
        <CardTitle className="text-xl font-semibold text-gray-800">Energy Usage by Device Type</CardTitle>
        </CardHeader>
        <CardContent>
        <div className="chart-container">
        {Object.keys(deviceTypeData).length > 0 ? (
          <PieChart
          data={Object.entries(deviceTypeData).map(([name, usage]) => ({
            name,
            usage: Number.parseFloat(usage.toFixed(2)),
          }))}
          />
        ) : (
        <p className="text-center text-gray-500">No data available for the selected time range</p>
        )}
      </div>
      </CardContent>
      </Card>
      <Card>
      <CardHeader>
      <CardTitle className="text-xl font-semibold text-gray-800">Total Energy Consumption Trend</CardTitle>
      </CardHeader>
      <CardContent>
      <div className="chart-container">
      {deviceData.length > 0 ? (
        <LineChart data={deviceData} />
      ) : (
      <p className="text-center text-gray-500">No data available for the selected time range</p>
      )}
    </div>
    </CardContent>
    </Card>
    </TabsContent>
    </Tabs>
    </motion.div>
    </motion.div>
    </div>
    </div>
              );
}
