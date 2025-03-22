// app/dashboard/page.tsx
"use client";

import { useState, useEffect } from "react";
import { Loader2, ZapOff, Activity } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface UsageData {
  device_id?: string;
  timestamp: string;
  energy_consumed: number;
}

interface ProcessedData {
  name: string;
  value: number;
}

interface EnergyConsumptionProps {
  userId?: string;
  token?: string;
  apiUrl?: string;
}

export function EnergyConsumption({ userId, token, apiUrl = 'http://localhost:8000/api/v1' }: EnergyConsumptionProps) {
  const [timeFrame, setTimeFrame] = useState("week");
  const [usageData, setUsageData] = useState<ProcessedData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalConsumption, setTotalConsumption] = useState(0);

  useEffect(() => {
    const fetchUsageData = async () => {
      if (!userId || !token) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        
        // Calculate date range based on selected timeframe
        const endDate = new Date();
        const startDate = new Date();
        
        switch (timeFrame) {
          case "day":
            startDate.setHours(0, 0, 0, 0);
            break;
          case "week":
            startDate.setDate(startDate.getDate() - 7);
            break;
          case "month":
            startDate.setMonth(startDate.getMonth() - 1);
            break;
          case "year":
            startDate.setFullYear(startDate.getFullYear() - 1);
            break;
        }
        
        // Format dates for API request
        const startDateStr = startDate.toISOString();
        const endDateStr = endDate.toISOString();
        
        // Fetch energy usage data
        const response = await fetch(`${apiUrl}/usage?start_time=${startDateStr}&end_time=${endDateStr}`, {
          headers: {
            'Authorization': `Basic ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error(`Error fetching usage data: ${response.status}`);
        }

        const data: UsageData[] = await response.json();
        
        // Process the data for chart display
        const processedData = processUsageData(data, timeFrame);
        setUsageData(processedData);
        
        // Calculate total consumption
        const total = data.reduce((sum, item) => sum + (item.energy_consumed || 0), 0);
        setTotalConsumption(total);
      } catch (err) {
        console.error("Failed to fetch usage data:", err);
        setError("Failed to load energy data. Please try again.");
        
        // Set fallback data for development
        const fallbackData = generateFallbackData(timeFrame);
        setUsageData(fallbackData);
        setTotalConsumption(fallbackData.reduce((sum, item) => sum + item.value, 0));
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsageData();
  }, [userId, token, timeFrame, apiUrl]);

  // Process raw usage data into chart-friendly format
  const processUsageData = (data: UsageData[], timeFrame: string): ProcessedData[] => {
    // Sort data by timestamp
    const sortedData = [...data].sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
    
    // Group data based on timeframe
    const groupedData: Record<string, number> = {};
    
    sortedData.forEach(item => {
      const date = new Date(item.timestamp);
      let key = '';
      
      switch (timeFrame) {
        case "day":
          key = `${date.getHours()}:00`;
          break;
        case "week":
          key = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][date.getDay()];
          break;
        case "month":
          key = `${date.getDate()}`;
          break;
        case "year":
          key = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][date.getMonth()];
          break;
      }
      
      groupedData[key] = (groupedData[key] || 0) + (item.energy_consumed || 0);
    });
    
    // Convert to array format for chart
    const result: ProcessedData[] = Object.entries(groupedData).map(([name, value]) => ({
      name,
      value: Number(value.toFixed(2))
    }));
    
    return result;
  };

  // Generate fallback data for development
  const generateFallbackData = (timeFrame: string): ProcessedData[] => {
    switch (timeFrame) {
      case "day":
        return Array.from({ length: 24 }, (_, i) => ({
          name: `${i}:00`,
          value: Math.floor(Math.random() * 20) + 5
        }));
      case "week":
        return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map(day => ({
          name: day,
          value: Math.floor(Math.random() * 100) + 20
        }));
      case "month":
        return Array.from({ length: 30 }, (_, i) => ({
          name: `${i + 1}`,
          value: Math.floor(Math.random() * 40) + 10
        }));
      case "year":
        return ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].map(month => ({
          name: month,
          value: Math.floor(Math.random() * 400) + 100
        }));
      default:
        return [];
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-4 h-full">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500 mb-2" />
        <p className="text-sm text-gray-500">Loading energy data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-4 h-full">
        <ZapOff className="w-8 h-8 text-red-500 mb-2" />
        <p className="text-sm text-gray-500">{error}</p>
        <Button 
          variant="outline" 
          size="sm" 
          className="mt-2"
          onClick={() => setIsLoading(true)}
        >
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Energy Consumption</h3>
        <Select
          value={timeFrame}
          onValueChange={setTimeFrame}
        >
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Select timeframe" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="day">Day</SelectItem>
            <SelectItem value="week">Week</SelectItem>
            <SelectItem value="month">Month</SelectItem>
            <SelectItem value="year">Year</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div className="grid grid-cols-2 gap-2 mb-4">
        <Card className="p-3">
          <p className="text-xs text-gray-500">Est. Cost</p>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold">${(totalConsumption * 0.23).toFixed(2)}</span>
            <span className="text-xs ml-1">USD</span>
          </div>
        </Card>
        <Card className="p-3">
          <p className="text-xs text-gray-500">Total Consumption</p>
          <div className="flex items-baseline">
            <span className="text-2xl font-bold">{totalConsumption.toFixed(1)}</span>
            <span className="text-xs ml-1">kWh</span>
          </div>
        </Card>
      </div>
      
      <Card className="p-4">
        <div className="h-64">
          {usageData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={usageData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip 
                  formatter={(value) => [`${value} kWh`, 'Energy']}
                  labelFormatter={(label) => `${label}`}
                />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex flex-col items-center justify-center h-full">
              <Activity className="h-8 w-8 text-gray-400 mb-2" />
              <p className="text-sm text-gray-500">No energy data available for this period</p>
            </div>
          )}
        </div>
      </Card>
      
      <div className="text-xs text-gray-500 text-center mt-2">
        Data shown is based on connected smart devices in your home
      </div>
    </div>
  );
}

export default function DashboardPage() {
  // You would typically get these from your auth context/provider
  const userId = "user123"; // Example user ID
  const token = "dXNlcjEyMzpwYXNzd29yZA=="; // Example token (Base64 encoded username:password)
  
  return (
    <div className="container mx-auto py-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <EnergyConsumption userId={userId} token={token} />
        </div>
        <div>
          {/* Other dashboard components can go here */}
        </div>
      </div>
    </div>
  );
}
