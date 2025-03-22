// components/energy-consumption.tsx
import { useState, useEffect } from "react";
import { CircleOff, Zap } from "lucide-react";
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface UsageData {
  date: string;
  energy: number;
}

interface EnergyConsumptionProps {
  userId: string;
  createAuthHeaders: () => Record<string, string>;
  apiUrl: string;
  isDarkMode?: boolean;
}

export function EnergyConsumption({ userId, createAuthHeaders, apiUrl, isDarkMode = false }: EnergyConsumptionProps) {
  const [data, setData] = useState<UsageData[]>([]);
  const [totalEnergy, setTotalEnergy] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEnergyData = async () => {
      if (!userId) return;

      try {
        setLoading(true);
        
        // Get date range for the last 7 days
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - 7);
        
        // Format dates for API query
        const start = startDate.toISOString();
        const end = endDate.toISOString();
        
        // Get all user's devices
        const devicesResponse = await fetch(`${apiUrl}/devices?user_id=${userId}`, {
          headers: createAuthHeaders()
        });
        
        if (!devicesResponse.ok) {
          throw new Error(`Error fetching devices: ${devicesResponse.statusText}`);
        }
        
        const devices = await devicesResponse.json();
        
        // Get usage data for all devices
        let allUsageData: any[] = [];
        
        for (const device of devices) {
          const usageResponse = await fetch(
            `${apiUrl}/usage?device_id=${device.id}&start_time=${start}&end_time=${end}`, 
            {
              headers: createAuthHeaders()
            }
          );
          
          if (usageResponse.ok) {
            const deviceUsage = await usageResponse.json();
            allUsageData = [...allUsageData, ...deviceUsage];
          }
        }
        
        // Process usage data by day
        const processedData = processUsageData(allUsageData);
        setData(processedData);
        
        // Calculate total energy
        const total = processedData.reduce((sum, item) => sum + item.energy, 0);
        setTotalEnergy(parseFloat(total.toFixed(2)));
        
      } catch (error) {
        console.error("Error fetching energy data:", error);
        setError("Failed to load energy data");
        
        // Set fallback data
        const fallbackData = generateFallbackData();
        setData(fallbackData);
        setTotalEnergy(fallbackData.reduce((sum, item) => sum + item.energy, 0));
      } finally {
        setLoading(false);
      }
    };
    
    fetchEnergyData();
  }, [userId, apiUrl, createAuthHeaders]);
  
  // Process raw usage data into daily totals
  const processUsageData = (rawData: any[]): UsageData[] => {
    // Group by date
    const dailyData: Record<string, number> = {};
    
    rawData.forEach(record => {
      try {
        const date = new Date(record.timestamp);
        const dateString = date.toISOString().split('T')[0]; // YYYY-MM-DD
        const energy = record.energy_consumed || 0;
        
        if (dailyData[dateString]) {
          dailyData[dateString] += energy;
        } else {
          dailyData[dateString] = energy;
        }
      } catch (e) {
        console.error("Error processing record:", e);
      }
    });
    
    // Convert to array and sort by date
    return Object.entries(dailyData)
      .map(([date, energy]) => ({
        date: formatDate(date),
        energy: parseFloat(energy.toFixed(2))
      }))
      .sort((a, b) => a.date.localeCompare(b.date));
  };
  
  // Generate fallback data if API fails
  const generateFallbackData = (): UsageData[] => {
    const data: UsageData[] = [];
    const today = new Date();
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      
      data.push({
        date: formatDate(date.toISOString().split('T')[0]),
        energy: Math.random() * 10 + 5 // Random value between 5-15
      });
    }
    
    return data;
  };
  
  // Format date for display
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Custom tooltip for the chart
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className={`p-2 ${isDarkMode ? 'bg-gray-800' : 'bg-white'} border rounded shadow-sm`}>
          <p className="text-sm font-medium">{payload[0].payload.date}</p>
          <p className="text-sm">{`${payload[0].value} kWh`}</p>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <div className="space-y-2">
        <h3 className="text-sm font-medium">Energy Consumption</h3>
        <div className="animate-pulse">
          <div className="h-[140px] bg-gray-200 rounded-md"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-2">
        <h3 className="text-sm font-medium">Energy Consumption</h3>
        <div className={`p-4 rounded-md ${isDarkMode ? 'bg-red-900/20' : 'bg-red-50'} text-red-500`}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <h3 className="text-sm font-medium">Energy Consumption</h3>
        <div className="flex items-center space-x-1">
          <Zap className="w-4 h-4 text-blue-500" />
          <span className="text-sm font-medium">{totalEnergy} kWh</span>
        </div>
      </div>
      
      <div className="h-[140px]">
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={data}
              margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
            >
              <XAxis
                dataKey="date"
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 10 }}
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tick={{ fontSize: 10 }}
                tickFormatter={(value) => `${value}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <defs>
                <linearGradient id="colorEnergy" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0091FF" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#0091FF" stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="energy"
                stroke="#0091FF"
                strokeWidth={2}
                fill="url(#colorEnergy)"
                dot={{ r: 2 }}
                activeDot={{ r: 5 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <CircleOff className="mx-auto h-8 w-8 text-gray-400" />
              <p className="mt-2 text-sm text-gray-500">No energy data available</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
