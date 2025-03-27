"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { LineChart, BarChart, PieChart } from "@/components/charts";
import {
  ArrowDownToLine,
  Calendar,
  Check,
  ChevronLeft,
  ChevronRight,
  Clock,
  Download,
  Home,
  Loader2,
  Lock,
  Minus,
  Plus,
  PlusCircle,
  Power,
  RefreshCw,
  Database,
  Server,
  Smartphone,
  Sparkles,
  Zap,
  BarChart2,
  PieChartIcon,
  TrendingUp,
  Info,
  Lightbulb,
  Thermometer,
  Fan,
  Tv,
  ShieldAlert,
} from "lucide-react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useToast } from "@/components/ui/use-toast";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { NavigationSidebar } from "@/app/components/navigation-sidebar";
import { Switch } from "@/components/ui/switch";

// Energy rates in AED per kWh
const ENERGY_RATE = 0.45; // AED per kWh

interface Device {
  id: string;
  name: string;
  type: string;
  room: string;
  status: "on" | "off";
  powerConsumption: number;
  totalEnergyConsumed: number;
  lastStatusChange?: number;
  usageHistory?: {
    startTime: number;
    endTime?: number;
    powerConsumption: number;
    energyConsumed: number;
  }[];
}

interface Room {
  id: string;
  name: string;
}

interface EnergyData {
  timestamp: string;
  value: number;
  device?: string;
  room?: string;
}

interface DeviceTypeData {
  type: string;
  consumption: number;
  percentage: number;
}

interface RoomData {
  name: string;
  consumption: number;
  percentage: number;
}

interface StatisticsData {
  energyData: EnergyData[];
  deviceTypeData: DeviceTypeData[];
  roomData: RoomData[];
  totalEnergyConsumed: number;
  totalCost: number;
  mostActiveRoom: {
    name: string;
    consumption: number;
  };
  energySavings: number;
}

export default function StatisticsPage() {
  const router = useRouter();
  const [timeRange, setTimeRange] = useState("week");
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [statisticsData, setStatisticsData] = useState<StatisticsData | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [accessDenied, setAccessDenied] = useState(false);
  const [creatingTestData, setCreatingTestData] = useState(false);
  const { toast } = useToast();
  
  // New state to track if auto-refresh is enabled
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);

  // Function to get a human-readable label for time ranges
  const getTimeRangeLabel = (range: string): string => {
    switch(range) {
      case "day": return "Daily";
      case "week": return "Weekly";
      case "month": return "Monthly";
      case "year": return "Yearly";
      default: return "Custom";
    }
  };

  // Debug function to check all localStorage values
  useEffect(() => {
    console.log("---- STATISTICS DEBUG ----");
    console.log("localStorage keys:", Object.keys(localStorage));
    
    // Print key localStorage items
    const keysToCheck = [
      'currentUser', 
      'currentMember', 
      'generatedHouseholdId',
      'currentHouseholdId',
      'user_id',
      'household_id'
    ];
    
    keysToCheck.forEach(key => {
      const value = localStorage.getItem(key);
      if (value) {
        try {
          // Try to parse as JSON
          const parsed = JSON.parse(value);
          console.log(`localStorage[${key}]:`, parsed);
        } catch (e) {
          // If not JSON, show as-is
          console.log(`localStorage[${key}]:`, value);
        }
      } else {
        console.log(`localStorage[${key}]: not found`);
      }
    });
    
    console.log("-------------------------");
  }, []);

  // Check permissions for household members
  useEffect(() => {
    const checkPermissions = () => {
      try {
        // Get current member from localStorage
        const storedMember = localStorage.getItem("currentMember");
        const storedUser = localStorage.getItem("currentUser");
        
        // If user is admin (not a member), they always have access
        if (storedUser && !storedMember) {
          console.log("User is admin, access granted");
          setAccessDenied(false);
          return;
        }
        
        // If user is a household member, check permissions
        if (storedMember) {
          const currentMember = JSON.parse(storedMember);
          console.log("Checking permissions for household member:", currentMember);
          
          if (currentMember.permissions && !currentMember.permissions.statisticalData) {
            console.error("Access denied: Member does not have statisticalData permission");
            setAccessDenied(true);
            
            // Show notification to user
            toast({
              title: "Access Denied",
              description: "You don't have permission to view statistics.",
              variant: "destructive",
            });
            
            // Redirect after a short delay
            setTimeout(() => {
              router.push("/dashboard");
            }, 2000);
            
            return;
          }
        }
        
        // If we got here, access is allowed
        setAccessDenied(false);
      } catch (error) {
        console.error("Error checking permissions:", error);
        // Default to allowing access if there's an error checking permissions
        setAccessDenied(false);
      }
    };
    
    // Run permission check
    checkPermissions();
    
    // Then try to fetch data only if access is not denied
    if (!accessDenied) {
      fetchData();
    }
  }, [router]); // Only run on initial mount

  const fetchData = useCallback(async () => {
    // Skip fetching if access is denied
    if (accessDenied) {
      console.log("Skipping data fetch - access denied");
      return;
    }
    
    try {
      setIsRefreshing(true);
      console.log("Starting statistics data fetch...");

      // Try to get any user_id or household_id directly stored in localStorage first
      let userId = localStorage.getItem('user_id');
      let householdId = localStorage.getItem('household_id') || localStorage.getItem('currentHouseholdId');
      let foundValidIds = false;
      
      console.log("Initial IDs from localStorage:", {userId, householdId});

      // Get current user from localStorage
      const storedUser = localStorage.getItem("currentUser");
      if (storedUser) {
        try {
          const currentUser = JSON.parse(storedUser);
          console.log("Parsed currentUser:", currentUser);
          
          // Check all possible ID fields in admin user
          if (!userId) {
            userId = currentUser._id || currentUser.id || currentUser.user_id;
          }
          
          if (!householdId) {
            householdId = currentUser.household_id || currentUser.householdId;
          }
          
          console.log("Statistics using admin user:", {userId, householdId});
          if (userId || householdId) foundValidIds = true;
        } catch (e) {
          console.error("Error parsing currentUser:", e);
        }
      } 
      
      // If we still don't have a userId, try household member
      const storedMember = localStorage.getItem("currentMember");
      if (!foundValidIds && storedMember) {
        try {
          const currentMember = JSON.parse(storedMember);
          console.log("Parsed currentMember:", currentMember);
          
          // Try multiple possible ID fields for member
          if (!userId) {
            userId = currentMember._id || currentMember.id || currentMember.member_id || currentMember.user_id;
          }
          
          if (!householdId) {
            householdId = currentMember.household_id || currentMember.householdId;
          }
          
          console.log("Statistics using household member:", {userId, householdId});
          if (userId || householdId) foundValidIds = true;
        } catch (e) {
          console.error("Error parsing currentMember:", e);
        }
      }

      // Check for a generated or fallback household ID
      if (!foundValidIds) {
        const generatedHouseholdId = localStorage.getItem("generatedHouseholdId");
        if (generatedHouseholdId) {
          householdId = generatedHouseholdId;
          console.log("Using generated household ID:", householdId);
          foundValidIds = true;
        }
      }

      // Last resort - try extracting IDs from rooms data
      if (!foundValidIds) {
        try {
          const roomsData = localStorage.getItem("rooms");
          if (roomsData) {
            const rooms = JSON.parse(roomsData);
            if (rooms && rooms.length > 0) {
              // Try to extract IDs from the first room
              const firstRoom = rooms[0];
              householdId = householdId || firstRoom.household_id || firstRoom.householdId;
              userId = userId || firstRoom.user_id || firstRoom.userId;
              console.log("Extracted IDs from rooms data:", {userId, householdId});
              if (userId || householdId) foundValidIds = true;
            }
          }
        } catch (e) {
          console.error("Error getting IDs from rooms data:", e);
        }
      }

      if (!userId && !householdId) {
        console.error("No user ID or household ID available for statistics");
        toast({
          title: "Error",
          description: "User or household ID not found. Please log in again.",
          variant: "destructive",
        });
        setIsLoading(false);
        setIsRefreshing(false);
        return;
      }

      // First, calculate local device energy consumption to ensure UI is consistent
      try {
        const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]");
        
        // Check if we actually have any devices before calculating energy consumption
        if (storedDevices.length === 0) {
          console.log("No devices found - displaying empty statistics for new user");
          
          // Set empty statistics data for a new user
          setStatisticsData({
            energyData: [],
            deviceTypeData: [],
            roomData: [],
            totalEnergyConsumed: 0,
            totalCost: 0,
            mostActiveRoom: {
              name: "",
              consumption: 0
            },
            energySavings: 0
          });
          
          setLastUpdated(new Date());
          setIsLoading(false);
          setIsRefreshing(false);
          return;
        }
        
        let localTotalEnergy = 0;
        
        // Calculate energy for devices currently turned on
        storedDevices.forEach((device: any) => {
          if (device.status === "on" && device.lastStatusChange) {
            const timeOn = (Date.now() - device.lastStatusChange) / 1000 / 3600; // hours
            const powerConsumption = device.basePowerConsumption || device.powerConsumption || device.energy_usage_per_hour || 0;
            const currentConsumption = (powerConsumption * timeOn) / 1000; // kWh
            localTotalEnergy += currentConsumption;
          }
          
          // Add any already recorded energy consumption
          if (device.totalEnergyConsumed) {
            localTotalEnergy += device.totalEnergyConsumed;
          }
        });
        
        console.log("Local calculated total energy consumption:", localTotalEnergy.toFixed(2), "kWh");
      } catch (e) {
        console.error("Error calculating local energy consumption:", e);
      }
      
      // Now trigger statistics collection to ensure we have fresh data
      try {
        console.log("Triggering statistics collection before fetching...");
        const statsResponse = await fetch('/api/statistics/collect', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            userId: userId,
            householdId: householdId
          }),
        });
        
        if (!statsResponse.ok) {
          console.warn("Failed to trigger statistics collection, continuing with fetch:", await statsResponse.text());
        } else {
          console.log("Statistics collection triggered successfully");
          // Wait a moment for collection to finish
          await new Promise(resolve => setTimeout(resolve, 2000)); // Increased to 2 seconds for more reliable syncing
        }
      } catch (error) {
        console.warn("Error triggering statistics collection, continuing with fetch:", error);
      }

      // Add timestamp to prevent caching
      const timestamp = Date.now();
      
      // Build URL with available parameters
      let apiUrl = `/api/statistics?timeRange=${timeRange}&_t=${timestamp}`;
      
      // Add parameters based on what's available
      if (userId) apiUrl += `&userId=${encodeURIComponent(userId)}`;
      if (householdId) apiUrl += `&householdId=${encodeURIComponent(householdId)}`;
      
      console.log("Fetching statistics from:", apiUrl);
      
      // Fetch latest statistics data from API with cache control set to no-cache
      const response = await fetch(apiUrl, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`Failed to fetch statistics: ${response.status} ${response.statusText}`);
        console.error("Error details:", errorText);
        
        if (response.status === 400) {
          toast({
            title: "Missing Information",
            description: "User or household ID is required to view statistics.",
            variant: "destructive",
          });
        } else {
          toast({
            title: "Error",
            description: "Failed to load statistics. Please try again later.",
            variant: "destructive",
          });
        }
        
        setIsLoading(false);
        setIsRefreshing(false);
        return;
      }

      const data = await response.json();
      console.log("Received statistics data:", data);
      
      if (data && typeof data.totalEnergyConsumed === 'number') {
      setStatisticsData(data);
      setLastUpdated(new Date());
        console.log("Statistics data set successfully, energy consumed:", data.totalEnergyConsumed);
      } else {
        console.warn("Statistics API returned invalid data format:", data);
        toast({
          title: "Warning",
          description: "Statistics data has an unexpected format. The database may be empty.",
          variant: "destructive",
        });
      }

      setIsLoading(false);
      setIsRefreshing(false);
      
      // Show toast confirming refresh
      if (isRefreshing) {
        toast({
          title: "Data Updated",
          description: "Your energy statistics have been refreshed with the latest data.",
        });
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      toast({
        title: "Error fetching data",
        description: "Could not load your energy statistics. Please try again.",
        variant: "destructive",
      });
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [accessDenied, timeRange, toast, setIsRefreshing, setStatisticsData, setLastUpdated, setIsLoading]);

  useEffect(() => {
    // Initialize user from localStorage
    const storedUser = localStorage.getItem("currentUser");
    const storedMember = localStorage.getItem("currentMember");
    
    let initialUser = null;
    
    if (storedUser) {
      try {
      const currentUser = JSON.parse(storedUser);
        console.log("Statistics page - Admin user loaded:", currentUser);
        
        // Ensure admin has all permissions
        if (!currentUser.permissions || Object.keys(currentUser.permissions).length === 0) {
          console.log("Statistics page - Admin user missing permissions, adding defaults");
          
          // Create default permissions for admin
          const defaultPermissions = {
            notifications: true,
            energyAlerts: true,
            addAutomation: true,
            statisticalData: true,
            deviceControl: true,
            roomControl: true,
          };
          
          // Update user with default permissions
          const updatedUser = {
            ...currentUser,
            permissions: defaultPermissions
          };
          
          localStorage.setItem("currentUser", JSON.stringify(updatedUser));
          initialUser = updatedUser;
        } else {
          // Ensure statisticalData permission is enabled for admin
          if (currentUser.permissions.statisticalData !== true) {
            console.log("Statistics page - Enabling statisticalData permission for admin");
            const updatedPermissions = {
              ...currentUser.permissions,
              statisticalData: true
            };
            
            const updatedUser = {
              ...currentUser,
              permissions: updatedPermissions
            };
            
            localStorage.setItem("currentUser", JSON.stringify(updatedUser));
            initialUser = updatedUser;
          } else {
            initialUser = currentUser;
          }
        }
      } catch (e) {
        console.error("Error parsing currentUser:", e);
      }
    } else if (storedMember) {
      try {
      const currentMember = JSON.parse(storedMember);
        console.log("Statistics page - Member user loaded:", currentMember);
        
        // Ensure member has basic permissions
        if (!currentMember.permissions) {
          console.log("Statistics page - Member missing permissions, adding defaults");
          
          // Create default permissions for members
          const defaultPermissions = {
            notifications: true,
            energyAlerts: true,
            deviceControl: true,
            roomControl: false,
            addAutomation: false,
            statisticalData: true, // Allow access to statistics by default
          };
          
          // Update member with default permissions
          const updatedMember = {
            ...currentMember,
            permissions: defaultPermissions
          };
          
          localStorage.setItem("currentMember", JSON.stringify(updatedMember));
          initialUser = updatedMember;
        } else {
          // Ensure statisticalData permission is enabled for all users
          if (currentMember.permissions.statisticalData !== true) {
            console.log("Statistics page - Enabling statisticalData permission for member");
            const updatedPermissions = {
              ...currentMember.permissions,
              statisticalData: true
            };
            
            const updatedMember = {
              ...currentMember,
              permissions: updatedPermissions
            };
            
            localStorage.setItem("currentMember", JSON.stringify(updatedMember));
            initialUser = updatedMember;
          } else {
            initialUser = currentMember;
          }
        }
      } catch (e) {
        console.error("Error parsing currentMember:", e);
      }
    } else {
      // No user found, redirect to login
      console.log("Statistics page - No user found, redirecting to login");
      router.push("/auth/login");
      return;
    }

    // Set the user and then fetch data
    setUser(initialUser);
    
    if (initialUser) {
      console.log("Statistics page - User set, fetching data with ID:", 
        initialUser.id || initialUser._id || initialUser.user_id || initialUser.member_id,
        "Household ID:", initialUser.householdId || initialUser.household_id);
    }

    fetchData();
  }, [timeRange, router, toast]);

  // Format data for charts
  const formattedEnergyData = useMemo(() => {
    if (!statisticsData?.energyData?.length) return [];

    return statisticsData.energyData.map((data) => {
      const date = new Date(data.timestamp);
      let label = "";

      if (timeRange === "day") {
        label = date.getHours() + ":00";
      } else if (timeRange === "week") {
        label = date.toLocaleDateString("en-US", { weekday: "short" });
      } else if (timeRange === "month") {
        label = date.getDate().toString();
      } else {
        label = date.toLocaleDateString("en-US", { month: "short" });
      }

      return {
        name: label,
        usage: Number(data.value.toFixed(2)),
      };
    });
  }, [statisticsData?.energyData, timeRange]);

  const formattedDeviceTypeData = useMemo(() => {
    if (!statisticsData?.deviceTypeData?.length) return [];

    return statisticsData.deviceTypeData.map((data) => ({
      name: data.type.charAt(0).toUpperCase() + data.type.slice(1),
      usage: Number(data.consumption.toFixed(2)),
    }));
  }, [statisticsData?.deviceTypeData]);

  const formattedRoomData = useMemo(() => {
    if (!statisticsData?.roomData?.length) return [];

    return statisticsData.roomData.map((data) => ({
      name: data.name,
      usage: Number(data.consumption.toFixed(2)),
    }));
  }, [statisticsData?.roomData]);

  // Animation variants
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

  const handleExportPDF = async () => {
    try {
      if (!statisticsData) {
        toast({
          title: "Error",
          description: "No statistics data available to export.",
          variant: "destructive",
        });
        return;
      }

      toast({
        title: "Generating Report",
        description: "Your energy report is being generated on the server...",
        duration: 5000,
      });

      // Format date for report title
      const currentDate = new Date();
      const formattedDate = currentDate.toISOString().split('T')[0];

      // Get period dates
      const endDate = currentDate.toISOString().split('T')[0];
      let startDate;

      switch(timeRange) {
        case "day":
          startDate = new Date(currentDate.setDate(currentDate.getDate() - 1)).toISOString().split('T')[0];
        break;
        case "week":
          startDate = new Date(currentDate.setDate(currentDate.getDate() - 7)).toISOString().split('T')[0];
        break;
        case "month":
          startDate = new Date(currentDate.setMonth(currentDate.getMonth() - 1)).toISOString().split('T')[0];
        break;
        case "year":
          startDate = new Date(currentDate.setFullYear(currentDate.getFullYear() - 1)).toISOString().split('T')[0];
        break;
      }

      // Prepare the request body
      const requestBody = {
        title: `Energy Report - ${getTimeRangeLabel(timeRange)}`,
        format: "pdf",
        start_date: startDate,
        end_date: endDate,
        device_ids: [] // You can populate this with specific devices if needed
      };

      // Create the report on the backend
      const response = await fetch(`/api/reports/create?user_id=${user.id || user.email}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }

      const data = await response.json();
      const reportId = data.report_id;

      // Poll for report status until it's complete
      let isComplete = false;
      let attempts = 0;
      const maxAttempts = 30; // 30 x 2 seconds = 60 second timeout

      toast({
        title: "Processing",
        description: "Your report is being processed. This may take a moment...",
        duration: 10000,
      });

      while (!isComplete && attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds between checks

        const statusResponse = await fetch(`/api/reports/${reportId}`);
        if (!statusResponse.ok) {
          throw new Error(`Error checking report status: ${statusResponse.status}`);
        }

        const statusData = await statusResponse.json();

        if (statusData.status === "completed") {
          isComplete = true;
        } else if (statusData.status === "failed") {
          throw new Error(`Report generation failed: ${statusData.error_message || "Unknown error"}`);
        }

        attempts++;
      }

      if (!isComplete) {
        throw new Error("Report generation timed out. Please try again later.");
      }

      // Download the completed report
      toast({
        title: "Report Ready",
        description: "Downloading your report...",
        duration: 3000,
      });

      // Create a link to download the file
      const downloadLink = document.createElement('a');
      downloadLink.href = `/api/reports/${reportId}/download`;
      downloadLink.download = `energy-report-${timeRange}-${formattedDate}.pdf`;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);

      toast({
        title: "Success",
        description: "Your energy report has been downloaded successfully!",
      });

    } catch (error) {
      console.error('Error generating PDF:', error);
      toast({
        title: "Export Failed",
        description: error instanceof Error ? error.message : "Failed to generate report. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Handle data refresh
  const handleRefresh = async () => {
    toast({
      title: "Refreshing Data",
      description: "Fetching the latest energy statistics...",
      variant: "default",
    });

    setIsRefreshing(true);

    try {
      // Get current user info with better fallbacks
      let userId = null;
      let householdId = null;

      const storedUser = localStorage.getItem("currentUser");
      const storedMember = localStorage.getItem("currentMember");

      if (storedUser) {
        try {
          const currentUser = JSON.parse(storedUser);
          userId = currentUser.id || currentUser.user_id;
          householdId = currentUser.householdId || currentUser.household_id;
          console.log("Using admin user:", { userId, householdId });
        } catch (e) {
          console.error("Error parsing currentUser:", e);
        }
      } 

      if (!userId && storedMember) {
        try {
          const currentMember = JSON.parse(storedMember);
          userId = currentMember.id || currentMember.member_id || currentMember.email;
          householdId = currentMember.householdId || currentMember.household_id;
          console.log("Using household member:", { userId, householdId });
        } catch (e) {
          console.error("Error parsing currentMember:", e);
        }
      }

      // Check for fallback household ID if not found
      if (!householdId) {
        const generatedHouseholdId = localStorage.getItem("generatedHouseholdId");
        if (generatedHouseholdId) {
          householdId = generatedHouseholdId;
          console.log("Using generated householdId:", householdId);
        }
      }

      if (!userId && !householdId) {
        console.warn("No user ID or household ID found for statistics");
        toast({
          title: "Error",
          description: "User or household ID not found. Please log in again.",
          variant: "destructive",
        });
        setIsRefreshing(false);
        return;
      }

      // First, calculate local device energy consumption to display in the UI
      try {
        const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]");
        let localTotalEnergy = 0;

        // Process each device
        storedDevices.forEach((device: any) => {
          let deviceEnergy = 0;

          // Calculate energy for currently active devices
          if (device.status === "on" && device.lastStatusChange) {
            const timeOn = (Date.now() - device.lastStatusChange) / 1000 / 3600; // hours
            const powerConsumption = device.basePowerConsumption || device.powerConsumption || device.energy_usage_per_hour || 0;
            const currentConsumption = (powerConsumption * timeOn) / 1000; // kWh
            deviceEnergy += currentConsumption;
          }

          // Add any saved energy consumption
          if (device.totalEnergyConsumed) {
            deviceEnergy += device.totalEnergyConsumed;
          }

          localTotalEnergy += deviceEnergy;
        });

        console.log("Local calculated total energy consumption:", localTotalEnergy.toFixed(2), "kWh");

        // If we have local data, update the UI immediately while waiting for API
        if (localTotalEnergy > 0 && statisticsData) {
          // Create a temporary update with the current energy consumption
          const tempUpdate = {
            ...statisticsData,
            totalEnergyConsumed: localTotalEnergy,
            totalCost: localTotalEnergy * ENERGY_RATE
          };

          // Update UI immediately
          setStatisticsData(tempUpdate);
          setLastUpdated(new Date());
        }
      } catch (e) {
        console.error("Error calculating local energy consumption:", e);
      }

      // Trigger statistics collection to ensure backend is up to date
      try {
        console.log("Triggering statistics collection for refresh...");
        const statsResponse = await fetch('/api/statistics/collect', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            userId,
            householdId
          }),
        });

        if (!statsResponse.ok) {
          console.warn("Failed to trigger statistics collection, continuing with fetch:", await statsResponse.text());
        } else {
          console.log("Statistics collection triggered successfully");
          // Wait for backend to process 
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
      } catch (error) {
        console.warn("Error triggering statistics collection, continuing with fetch:", error);
      }

      // Add timestamp to prevent caching
      const timestamp = Date.now();

      // Build URL with available parameters
      let apiUrl = `/api/statistics?timeRange=${timeRange}&_t=${timestamp}`;

      // Add parameters based on what's available
      if (userId) apiUrl += `&userId=${encodeURIComponent(userId)}`;
      if (householdId) apiUrl += `&householdId=${encodeURIComponent(householdId)}`;

      console.log("Refreshing statistics from:", apiUrl);

      // Fetch latest statistics data from API with no-cache settings
      const response = await fetch(apiUrl, {
        cache: 'no-store',
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Statistics API error:", response.status, response.statusText);
        console.error("Error details:", errorText);
        throw new Error(`Failed to fetch statistics: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("Received statistics data:", data);

      // Check if data contains energy information
      if (data && typeof data.totalEnergyConsumed === 'number') {
        setStatisticsData(data);
        setLastUpdated(new Date());

        toast({
          title: "Data Refreshed",
          description: `Energy consumed: ${data.totalEnergyConsumed.toFixed(2)} kWh`,
          variant: "default",
        });
      } else {
        console.warn("Invalid statistics data:", data);
        toast({
          title: "Warning",
          description: "Statistics data format is unexpected. Please try again.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Error refreshing statistics:', error);
      toast({
        title: "Refresh Failed",
        description: "Could not refresh statistics data. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  // Handle access request
  const handleRequestAccess = () => {
    toast({
      title: "Access Requested",
      description: "Your request for access to statistical data has been sent to the admin.",
    });
  };

  // Function to create test devices with energy usage data
  const createTestDevices = async () => {
    try {
      setCreatingTestData(true);

      // Get user and household IDs
      let userId = null;
      let householdId = null;

      // Try to get from localStorage
      const storedUser = localStorage.getItem("currentUser");
      const storedMember = localStorage.getItem("currentMember");

      if (storedUser) {
        try {
          const currentUser = JSON.parse(storedUser);
          userId = currentUser._id || currentUser.id || currentUser.user_id;
          householdId = currentUser.household_id || currentUser.householdId;
        } catch (e) {
          console.error("Error parsing currentUser:", e);
        }
      } else if (storedMember) {
        try {
          const currentMember = JSON.parse(storedMember);
          userId = currentMember._id || currentMember.id || currentMember.member_id || currentMember.user_id;
          householdId = currentMember.household_id || currentMember.householdId;
        } catch (e) {
          console.error("Error parsing currentMember:", e);
        }
      }

      if (!userId) {
        userId = localStorage.getItem('user_id');
      }

      if (!householdId) {
        householdId = localStorage.getItem('household_id') || localStorage.getItem('currentHouseholdId') || localStorage.getItem('generatedHouseholdId');
      }

      if (!userId && !householdId) {
        // Generate a fake household ID if nothing else available
        householdId = "test-household-" + Date.now();
        localStorage.setItem('generatedHouseholdId', householdId);
      }

      // Create sample rooms
      const rooms = [
        { name: "Living Room", household_id: householdId, user_id: userId },
        { name: "Kitchen", household_id: householdId, user_id: userId },
        { name: "Bedroom", household_id: householdId, user_id: userId },
        { name: "Bathroom", household_id: householdId, user_id: userId },
        { name: "Office", household_id: householdId, user_id: userId }
      ];

      // Save rooms to localStorage for frontend use
      localStorage.setItem('rooms', JSON.stringify(rooms));

      // Create sample devices with energy usage data
      const devices = [
        { 
          name: "Living Room Light", 
          type: "lightbulb", 
          room: "Living Room", 
          status: "on", 
          energy_usage_per_hour: 60, // 60W
          last_status_change: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(), // 3 hours ago
          household_id: householdId,
          user_id: userId
        },
        { 
          name: "TV", 
          type: "tv", 
          room: "Living Room", 
          status: "on", 
          energy_usage_per_hour: 120, // 120W
          last_status_change: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
          household_id: householdId,
          user_id: userId
        },
        { 
          name: "Air Conditioner", 
          type: "ac", 
          room: "Bedroom", 
          status: "on", 
          energy_usage_per_hour: 1200, // 1200W
          last_status_change: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(), // 5 hours ago
          household_id: householdId,
          user_id: userId
        },
        { 
          name: "Fridge", 
          type: "fridge", 
          room: "Kitchen", 
          status: "on", 
          energy_usage_per_hour: 150, // 150W
          last_status_change: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(), // 2 days ago
          household_id: householdId,
          user_id: userId
        },
        { 
          name: "Computer", 
          type: "computer", 
          room: "Office", 
          status: "on", 
          energy_usage_per_hour: 300, // 300W
          last_status_change: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(), // 4 hours ago
          household_id: householdId,
          user_id: userId
        }
      ];

      // Save devices to localStorage for frontend use
      localStorage.setItem('devices', JSON.stringify(devices));

      // Now send data to backend via API
      const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

      // Add rooms to backend
      for (const room of rooms) {
        try {
          const response = await fetch(`${BACKEND_URL}/api/rooms`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(room),
          });

          if (!response.ok) {
            console.error(`Failed to add room ${room.name}:`, await response.text());
          }
        } catch (error) {
          console.error(`Error adding room ${room.name}:`, error);
        }
      }

      // Add devices to backend
      for (const device of devices) {
        try {
          const response = await fetch(`${BACKEND_URL}/api/user/devices`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(device),
          });

          if (!response.ok) {
            console.error(`Failed to add device ${device.name}:`, await response.text());
          }
        } catch (error) {
          console.error(`Error adding device ${device.name}:`, error);
        }
      }

      // Trigger statistics collection
      try {
        console.log("Triggering statistics collection...");
        const statsResponse = await fetch('/api/statistics/collect', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            userId: userId,
            householdId: householdId
          }),
        });

        if (!statsResponse.ok) {
          console.error("Failed to trigger statistics collection:", await statsResponse.text());
        } else {
          console.log("Statistics collection triggered successfully");
        }
      } catch (error) {
        console.error("Error triggering statistics collection:", error);
      }

      // Show success message
      toast({
        title: "Test data created",
        description: `Created ${rooms.length} rooms and ${devices.length} devices with energy usage data`,
      });

      // Refresh data
      await fetchData();

    } catch (error) {
      console.error("Error creating test data:", error);
      toast({
        title: "Error",
        description: "Failed to create test data",
        variant: "destructive",
      });
    } finally {
      setCreatingTestData(false);
    }
  };

  if (!user) return null;

  // Check if user has permission to view statistics
  if (user.permissions && user.permissions.statisticalData === false) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
      <NavigationSidebar />
      <div className="flex-1 ml-[72px] p-6 flex items-center justify-center">
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
    id="statistics-container"
    >
    <motion.header variants={itemVariants} className="flex justify-between items-center mb-8">
    <div className="flex items-center gap-4">
    <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
    <BarChart2 className="h-6 w-6 text-white" />
    </div>
    <div>
    <h1 className="text-2xl font-bold text-gray-800">Energy Statistics</h1>
    <p className="text-sm text-gray-500">
    Monitor and analyze your energy consumption
    {lastUpdated && (
      <span className="text-xs ml-2 text-muted-foreground">
      · Last updated: {lastUpdated.toLocaleTimeString()}
      </span>
    )}
    </p>
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
    onClick={handleRefresh}
    disabled={isRefreshing}
    className="text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF] hover:text-white"
    >
    {isRefreshing ? <Loader2 className="h-5 w-5 animate-spin" /> : <RefreshCw className="h-5 w-5" />}
    </Button>
    <Button
    variant="outline"
    size="icon"
    onClick={handleExportPDF}
    className="text-[#FF9500] border-[#FF9500] hover:bg-[#FF9500] hover:text-white"
    >
    <Download className="h-5 w-5" />
    </Button>
    <TooltipProvider>
    <Tooltip>
    <TooltipTrigger asChild>
    <Button
    variant="secondary"
    onClick={createTestDevices}
    disabled={creatingTestData}
    >
    {creatingTestData ? (
      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
    ) : (
    <PlusCircle className="mr-2 h-4 w-4" />
    )}
    Create Test Data
    </Button>
    </TooltipTrigger>
    <TooltipContent side="bottom">
    <p>Create test devices with energy usage data</p>
    </TooltipContent>
    </Tooltip>
    </TooltipProvider>
    </div>
    </motion.header>

    {isLoading || !statisticsData ? (
      // Loading state
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {[1, 2, 3].map((i) => (
        <Skeleton key={i} className="h-[150px] rounded-xl" />
      ))}
      <Skeleton className="h-[400px] col-span-full rounded-xl" />
      </div>
    ) : statisticsData.energyData.length === 0 && statisticsData.deviceTypeData.length === 0 ? (
    // No data state
    <div className="flex flex-col items-center justify-center h-96 text-center p-8" id="statistics-container">
    <Database className="h-16 w-16 text-muted-foreground mb-4" />
    <h3 className="text-xl font-semibold mb-2">No Energy Data Available</h3>
    <p className="text-muted-foreground mb-6 max-w-md">
    We couldn't find any active devices tracking energy usage. 
      {lastUpdated && (
        <span className="block text-xs mt-2">
        Last checked: {lastUpdated.toLocaleString()}
        </span>
    )}
    </p>

    <div className="space-y-4 mb-8">
    <div className="flex items-center text-sm">
    <PlusCircle className="h-5 w-5 mr-3 text-primary" />
    <span>Add some devices to your smart home</span>
    </div>
    <div className="flex items-center text-sm">
    <Power className="h-5 w-5 mr-3 text-amber-500" />
    <span>Turn on your devices to start tracking energy usage</span>
    </div>
    <div className="flex items-center text-sm">
    <Clock className="h-5 w-5 mr-3 text-blue-500" />
    <span>Let them run for a while to collect usage data</span>
      </div>
    </div>

    <div className="flex space-x-4">
    <Button 
    variant="default" 
    onClick={() => router.push('/devices')}
    className="flex items-center"
    >
    <PlusCircle className="mr-2 h-4 w-4" />
    Add Device
    </Button>
    <Button 
    variant="outline" 
    onClick={handleRefresh} 
    disabled={isRefreshing}
    className="flex items-center"
    >
    {isRefreshing ? (
      <>
      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      Refreshing...
        </>
    ) : (
    <>
    <RefreshCw className="mr-2 h-4 w-4" />
    Refresh Data
    </>
    )}
    </Button>
    </div>
    </div>
    ) : (
    <>
    {/* Summary Cards */}
    <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
    <motion.div variants={itemVariants}>
    <Card className="bg-gradient-to-br from-[#00B2FF] to-[#0085FF] text-white overflow-hidden">
    <CardHeader className="pb-2">
    <CardTitle className="text-lg font-medium flex items-center justify-between">
    <div className="flex items-center">
    <Zap className="h-5 w-5 mr-2" />
    Total Energy Consumed
    </div>
    <Button 
    variant="ghost" 
    size="sm" 
    className="text-white hover:bg-white/20 -mt-2 -mr-2 h-8 w-8 p-0"
    onClick={handleRefresh}
    disabled={isRefreshing}
    >
    {isRefreshing ? 
      <Loader2 className="h-4 w-4 animate-spin" /> : 
      <RefreshCw className="h-4 w-4" />
    }
    </Button>
    </CardTitle>
    </CardHeader>
    <CardContent>
    <div className="text-3xl font-bold">{statisticsData.totalEnergyConsumed.toFixed(2)} kWh</div>
    <div className="flex items-center mt-2">
    <Badge className="bg-white/20 hover:bg-white/30 text-white">
    {timeRange === "day"
      ? "Today"
      : timeRange === "week"
        ? "This Week"
        : timeRange === "month"
          ? "This Month"
          : "This Year"}
          </Badge>
          {statisticsData.energySavings > 0 && (
            <Badge className="bg-green-500/20 hover:bg-green-500/30 text-white ml-2">
            {statisticsData.energySavings}% saved
            </Badge>
          )}
          </div>
          <div className="mt-4">
          <div className="flex justify-between items-center">
          <span className="text-xs text-gray-500">Real-time Data</span>
          <span className="text-xs text-gray-500">Updated: {lastUpdated?.toLocaleTimeString()}</span>
          </div>
          <Progress value={100} className="h-2 bg-white/20" />
          </div>
          </CardContent>
          </Card>
          </motion.div>

          <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-br from-[#FF9500] to-[#FFB800] text-white overflow-hidden">
          <CardHeader className="pb-2">
          <CardTitle className="text-lg font-medium flex items-center">
          <Calendar className="h-5 w-5 mr-2" />
          Total Cost
          </CardTitle>
          </CardHeader>
          <CardContent>
          <div className="text-3xl font-bold">{statisticsData.totalCost.toFixed(2)} AED</div>
          <p className="text-sm opacity-80 mt-2">based on current energy rates</p>

          <div className="mt-4 bg-white/10 rounded-lg p-3">
          <div className="flex justify-between items-center">
          <span className="text-sm">Projected Monthly</span>
          <span className="font-semibold">
          {(
            statisticsData.totalCost * (timeRange === "day" ? 30 : timeRange === "week" ? 4 : 1)
          ).toFixed(2)}{" "}
          AED
          </span>
          </div>
          </div>
          </CardContent>
          </Card>
          </motion.div>

          <motion.div variants={itemVariants}>
          <Card className="bg-gradient-to-br from-[#00B2FF] to-[#0085FF] text-white overflow-hidden">
          <CardHeader className="pb-2">
          <CardTitle className="text-lg font-medium flex items-center">
          <TrendingUp className="h-5 w-5 mr-2" />
          Most Active Room
          </CardTitle>
          </CardHeader>
          <CardContent>
          <div className="text-3xl font-bold">{statisticsData.mostActiveRoom.name}</div>
          <div className="flex justify-between items-center mt-2">
          <span className="text-sm opacity-80">Energy Consumption</span>
          <Badge className="bg-white/20 hover:bg-white/30 text-white">
          {statisticsData.mostActiveRoom.consumption.toFixed(2)} kWh
          </Badge>
          </div>

          <div className="mt-4">
          <div className="flex justify-between text-sm mb-1">
          <span>Room Efficiency</span>
          <span>{statisticsData.mostActiveRoom.consumption > 20 ? "Needs Improvement" : "Good"}</span>
          </div>
          <Progress
          value={100 - Math.min(100, (statisticsData.mostActiveRoom.consumption / 30) * 100)}
          className="h-2 bg-white/20"
          />
          </div>
          </CardContent>
          </Card>
          </motion.div>
          </motion.div>

          {/* Main Content */}
          <motion.div variants={itemVariants}>
          <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-white shadow-md rounded-lg p-1">
          <TabsTrigger
          value="overview"
          className="data-[state=active]:bg-[#00B2FF] data-[state=active]:text-white"
          >
          <TrendingUp className="h-4 w-4 mr-2" />
          Overview
          </TabsTrigger>
          <TabsTrigger
          value="devices"
          className="data-[state=active]:bg-[#00B2FF] data-[state=active]:text-white"
          >
          <Smartphone className="h-4 w-4 mr-2" />
          Devices
          </TabsTrigger>
          <TabsTrigger
          value="rooms"
          className="data-[state=active]:bg-[#00B2FF] data-[state=active]:text-white"
          >
          <PieChartIcon className="h-4 w-4 mr-2" />
          Rooms
          </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
          <Card>
          <CardHeader>
          <CardTitle className="text-xl font-semibold text-gray-800 flex items-center">
          Energy Consumption Trend
          <TooltipProvider>
          <Tooltip>
          <TooltipTrigger asChild>
          <Info className="h-4 w-4 ml-2 text-gray-400" />
          </TooltipTrigger>
          <TooltipContent>
          <p>Energy consumption in kWh over time</p>
          </TooltipContent>
          </Tooltip>
          </TooltipProvider>
          </CardTitle>
          <CardDescription>
          {timeRange === "day"
            ? "Hourly consumption for the past 24 hours"
            : timeRange === "week"
              ? "Daily consumption for the past week"
              : timeRange === "month"
                ? "Daily consumption for the past month"
                : "Monthly consumption for the past year"}
                </CardDescription>
                </CardHeader>
                <CardContent className="h-[350px]">
                <div className="chart-container h-full">
                <LineChart
                data={formattedEnergyData}
                xAxisLabel={
                  timeRange === "day"
                    ? "Hour"
                    : timeRange === "week"
                      ? "Day"
                      : timeRange === "month"
                        ? "Date"
                        : "Month"
                }
                yAxisLabel="kWh"
                className="h-full"
                />
                </div>
                </CardContent>
                </Card>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800">
                Energy Usage by Device Type
                </CardTitle>
                </CardHeader>
                <CardContent className="h-[300px]">
                <div className="chart-container h-full">
                <PieChart 
                data={formattedDeviceTypeData} 
                valueFormat={(value) => `${value} kWh`} 
                />
                </div>
                </CardContent>
                </Card>

                <Card>
                <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800">
                Cost Breakdown by Device Type
                </CardTitle>
                </CardHeader>
                <CardContent className="h-[300px]">
                {formattedDeviceTypeData.length > 0 ? (
                  <div className="chart-container h-full">
                  <PieChart
                  data={formattedDeviceTypeData.map(item => ({
                    name: item.name,
                    usage: Number((item.usage * ENERGY_RATE).toFixed(2)),
                  }))}
                  valueFormat={(value) => `${value} AED`}
                  />
                  </div>
                ) : (
                <div className="flex flex-col items-center justify-center h-full">
                <Smartphone className="h-12 w-12 text-gray-300 mb-4" />
                <p className="text-gray-500">No device data available</p>
                </div>
                )}
                </CardContent>
                </Card>
                </div>
                </TabsContent>

                {/* Devices Tab */}
                <TabsContent value="devices" className="space-y-6">
                <Card>
                <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800 flex items-center">
                Energy Usage by Device Type
                <TooltipProvider>
                <Tooltip>
                <TooltipTrigger asChild>
                <Info className="h-4 w-4 ml-2 text-gray-400" />
                </TooltipTrigger>
                <TooltipContent>
                <p>Energy consumption in kWh</p>
                </TooltipContent>
                </Tooltip>
                </TooltipProvider>
                </CardTitle>
                </CardHeader>
                <CardContent className="h-[400px]">
                {formattedDeviceTypeData.length > 0 ? (
                  <div className="chart-container h-full">
                  <BarChart data={formattedDeviceTypeData} />
                  </div>
                ) : (
                <div className="flex flex-col items-center justify-center h-full">
                <Smartphone className="h-12 w-12 text-gray-300 mb-4" />
                <p className="text-gray-500">No device data available</p>
                </div>
                )}
                </CardContent>
                </Card>

                <Card>
                <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800 flex items-center">
                Device Cost (AED)
                <TooltipProvider>
                <Tooltip>
                <TooltipTrigger asChild>
                <Info className="h-4 w-4 ml-2 text-gray-400" />
                </TooltipTrigger>
                <TooltipContent>
                <p>Cost in AED based on {ENERGY_RATE} AED/kWh</p>
                </TooltipContent>
                </Tooltip>
                </TooltipProvider>
                </CardTitle>
                </CardHeader>
                <CardContent className="h-[400px]">
                {formattedDeviceTypeData.length > 0 ? (
                  <div className="chart-container h-full">
                  <BarChart
                  data={formattedDeviceTypeData.map((device) => ({
                    name: device.name,
                    usage: device.usage * ENERGY_RATE,
                  }))}
                  yAxisLabel="AED"
                  />
                  </div>
                ) : (
                <div className="flex flex-col items-center justify-center h-full">
                <Smartphone className="h-12 w-12 text-gray-300 mb-4" />
                <p className="text-gray-500">No device data available</p>
                </div>
                )}
                </CardContent>
                </Card>

                <Card>
                <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800">Device Type Efficiency</CardTitle>
                <CardDescription>Energy consumption by device type with efficiency rating</CardDescription>
                </CardHeader>
                <CardContent>
                <div className="space-y-4">
                {statisticsData.deviceTypeData.map((device, index) => {
                  // Calculate efficiency score
                  const efficiency = 100 - Math.min(100, (device.consumption / 20) * 100)
                  const getEfficiencyColor = (score: number) => {
                    if (score > 75) return "text-green-500"
                      if (score > 50) return "text-yellow-500"
                        if (score > 25) return "text-red-500"
                          return "text-red-500"
                  }
                  const getEfficiencyLabel = (score: number) => {
                    if (score > 75) return "Excellent"
                      if (score > 50) return "Good"
                        if (score > 25) return "Fair"
                          return "Poor"
                  }

                  const getEfficiencyVariant = (score: number) => {
                    if (score > 75) return "excellent"
                      if (score > 50) return "good"
                        if (score > 25) return "fair"
                          return "poor"
                  }

                  // Get icon based on device type
                  let DeviceIcon = Smartphone
                  switch (device.type.toLowerCase()) {
                    case "light":
                      case "lightbulb":
                      DeviceIcon = Lightbulb
                    break
                    case "thermostat":
                      case "ac":
                      DeviceIcon = Thermometer
                    break
                    case "fan":
                      DeviceIcon = Fan
                    break
                    case "tv":
                      DeviceIcon = Tv
                    break
                  }

                  return (
                    <div key={index} className="bg-white p-4 rounded-lg shadow-sm device-efficiency-card">
                    <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                    <DeviceIcon className="h-5 w-5 text-[#00B2FF]" />
                    </div>
                    <div>
                    <h3 className="font-medium capitalize">{device.type}</h3>
                    <p className="text-sm text-gray-500">
                    {device.consumption.toFixed(2)} kWh ({device.percentage.toFixed(1)}%)
                    </p>
                    </div>
                    </div>
                    <div className="text-right">
                    <span className={`font-medium ${getEfficiencyColor(efficiency)}`}>
                    {getEfficiencyLabel(efficiency)}
                    </span>
                    <p className="text-sm text-gray-500">{efficiency.toFixed(0)}% efficient</p>
                    </div>
                    </div>
                    <Progress 
                    value={efficiency} 
                    className="h-2" 
                    variant={getEfficiencyVariant(efficiency) as "default" | "excellent" | "good" | "fair" | "poor"} 
                    />
                    </div>
                  )
                })}
                </div>
                </CardContent>
                </Card>
                </TabsContent>

                {/* Rooms Tab */}
                <TabsContent value="rooms" className="space-y-6">
                <Card>
                <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800 flex items-center">
                Energy Usage by Room
                <TooltipProvider>
                <Tooltip>
                <TooltipTrigger asChild>
                <Info className="h-4 w-4 ml-2 text-gray-400" />
                </TooltipTrigger>
                <TooltipContent>
                <p>Energy consumption in kWh</p>
                </TooltipContent>
                </Tooltip>
                </TooltipProvider>
                </CardTitle>
                </CardHeader>
                <CardContent className="h-[400px]">
                {formattedRoomData.length > 0 ? (
                  <div className="chart-container h-full">
                  <BarChart data={formattedRoomData} />
                  </div>
                ) : (
                <div className="flex flex-col items-center justify-center h-full">
                <Home className="h-12 w-12 text-gray-300 mb-4" />
                <p className="text-gray-500">No room data available</p>
                </div>
                )}
                </CardContent>
                </Card>

                <Card>
                <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800 flex items-center">
                Room Cost (AED)
                <TooltipProvider>
                <Tooltip>
                <TooltipTrigger asChild>
                <Info className="h-4 w-4 ml-2 text-gray-400" />
                </TooltipTrigger>
                <TooltipContent>
                <p>Cost in AED based on {ENERGY_RATE} AED/kWh</p>
                </TooltipContent>
                </Tooltip>
                </TooltipProvider>
                </CardTitle>
                </CardHeader>
                <CardContent className="h-[400px]">
                {formattedRoomData.length > 0 ? (
                  <div className="chart-container h-full">
                  <BarChart
                  data={formattedRoomData.map((room) => ({
                    name: room.name,
                    usage: room.usage * ENERGY_RATE,
                  }))}
                  yAxisLabel="AED"
                  />
                  </div>
                ) : (
                <div className="flex flex-col items-center justify-center h-full">
                <Home className="h-12 w-12 text-gray-300 mb-4" />
                <p className="text-gray-500">No room data available</p>
                </div>
                )}
                </CardContent>
                </Card>

                <Card>
                <CardHeader>
                <CardTitle className="text-xl font-semibold text-gray-800">Room Energy Distribution</CardTitle>
                <CardDescription>Percentage of total energy consumption by room</CardDescription>
                </CardHeader>
                <CardContent className="h-[400px]">
                {formattedRoomData.length > 0 ? (
                  <PieChart data={formattedRoomData} />
                ) : (
                <div className="flex flex-col items-center justify-center h-full">
                <Home className="h-12 w-12 text-gray-300 mb-4" />
                <p className="text-gray-500">No room data available</p>
                </div>
                )}
                </CardContent>
                </Card>
                </TabsContent>
                </Tabs>
                </motion.div>
                </>
    )}
    </motion.div>
    </div>
    </div>
  );
}
