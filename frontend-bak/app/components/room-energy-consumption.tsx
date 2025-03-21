"use client";

import { useState } from "react";
import { Loader2, ZapOff, ChevronRight } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

interface Room {
  id: string;
  name: string;
  consumption: number;
  devices?: string[];
}

interface RoomEnergyConsumptionProps {
  rooms: Room[];
  isLoading?: boolean;
  userId?: string;
  token?: string;
}

export function RoomEnergyConsumption({ rooms, isLoading = false, userId, token }: RoomEnergyConsumptionProps) {
  const router = useRouter();
  const [showAllRooms, setShowAllRooms] = useState(false);

  const sortedRooms = [...rooms].sort((a, b) => b.consumption - a.consumption);
  const displayRooms = showAllRooms ? sortedRooms : sortedRooms.slice(0, 4);
  
  const maxConsumption = Math.max(...rooms.map(room => room.consumption), 1);
  
  const getTotalConsumption = () => {
    return rooms.reduce((total, room) => total + room.consumption, 0);
  };
  
  const getColorForPercentage = (percentage: number) => {
    if (percentage < 30) return "bg-green-500";
    if (percentage < 70) return "bg-yellow-500";
    return "bg-red-500";
  };

  const handleViewRoom = (roomId: string) => {
    router.push(`/rooms/${roomId}`);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-32">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  if (rooms.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-4 h-32">
        <ZapOff className="w-8 h-8 text-gray-400 mb-2" />
        <p className="text-sm text-gray-500">No room data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <span className="text-2xl font-bold">{getTotalConsumption().toFixed(1)}</span>
          <span className="text-sm ml-1">kWh</span>
          <p className="text-xs text-gray-500">Total Consumption</p>
        </div>
        <div className="text-right">
          <span className="text-xl font-bold">${(getTotalConsumption() * 0.23).toFixed(2)}</span>
          <p className="text-xs text-gray-500">Estimated Cost</p>
        </div>
      </div>
      
      <div className="space-y-4">
        {displayRooms.map((room) => {
          const percentage = Math.min(100, Math.round((room.consumption / maxConsumption) * 100));
          const colorClass = getColorForPercentage(percentage);
          const deviceCount = room.devices?.length || 0;
          
          return (
            <div key={room.id} className="space-y-1">
              <div className="flex justify-between items-center">
                <div className="flex items-center">
                  <span className="font-medium">{room.name}</span>
                  <span className="ml-2 text-xs text-gray-500">{deviceCount} devices</span>
                </div>
                <div className="flex items-center">
                  <span className="font-medium mr-2">{room.consumption.toFixed(1)} kWh</span>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6"
                    onClick={() => handleViewRoom(room.id)}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <Progress 
                  value={percentage} 
                  className={`h-2 ${colorClass}`} 
                />
                <span className="text-xs w-8">{percentage}%</span>
              </div>
            </div>
          );
        })}
      </div>
      
      {rooms.length > 4 && (
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full mt-2"
          onClick={() => setShowAllRooms(!showAllRooms)}
        >
          {showAllRooms ? "Show Less" : `Show All (${rooms.length})`}
        </Button>
      )}
    </div>
  );
}
