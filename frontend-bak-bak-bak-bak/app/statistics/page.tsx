// statistics/page.tsx
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LineChart, BarChart, PieChart } from "@/components/charts";
import { Download, User, BarChart2, PieChartIcon, TrendingUp, Lock } from "lucide-react";
import { PDFDocument, rgb } from "pdf-lib";
import { toPng } from "html-to-image";
//import { Inter } from "next/font/google";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ui/use-toast";
import { NavigationSidebar } from "@/app/components/navigation-sidebar"; // Import the navbar

//const inter = Inter({ subsets: ["latin"] });

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
    //style.textContent = `
    //  @import url('https://fonts.googleapis.com/css2?family=Inter&display=swap');
    //  * { font-family: 'Inter', sans-serif; }
    //`;
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

export default function StatisticsPage() {
  const router = useRouter();
  const [devices, setDevices] = useState<Device[]>([]);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [timeRange, setTimeRange] = useState("day");
  const [user, setUser] = useState<any>(null);
  const { toast } = useToast();

  useEffect(() => {
    const currentUser = JSON.parse(localStorage.getItem("currentUser") || "{}");
    //if (!currentUser.id || !currentUser.permissions?.statisticalData) {
    //  router.push("/");
    //  return;
    //}
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
              <Button
                variant="outline"
                size="icon"
                onClick={() => generatePDF(devices, rooms)}
                className="text-[#FF9500] border-[#FF9500] hover:bg-[#FF9500] hover:text-white"
              >
                <Download className="h-5 w-5" />
              </Button>
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
                    {deviceData.length > 0 ? (
                      <BarChart data={deviceData} />
                    ) : (
                      <p className="text-center text-gray-500">No data available for the selected time range</p>
                    )}
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xl font-semibold text-gray-800">Device Usage Over Time</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {deviceData.length > 0 ? (
                      <LineChart data={deviceData} />
                    ) : (
                      <p className="text-center text-gray-500">No data available for the selected time range</p>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="rooms" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xl font-semibold text-gray-800">Energy Usage by Room</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {roomData.length > 0 ? (
                      <BarChart data={roomData} />
                    ) : (
                      <p className="text-center text-gray-500">No data available for the selected time range</p>
                    )}
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xl font-semibold text-gray-800">Room Usage Over Time</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {roomData.length > 0 ? (
                      <LineChart data={roomData} />
                    ) : (
                      <p className="text-center text-gray-500">No data available for the selected time range</p>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
              <TabsContent value="overview" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xl font-semibold text-gray-800">Energy Usage by Device Type</CardTitle>
                  </CardHeader>
                  <CardContent>
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
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-xl font-semibold text-gray-800">Total Energy Consumption Trend</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {deviceData.length > 0 ? (
                      <LineChart data={deviceData} />
                    ) : (
                      <p className="text-center text-gray-500">No data available for the selected time range</p>
                    )}
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
