// components/room-energy-consumption.tsx
import { useState } from "react";
import { LightbulbIcon, DoorOpen, Laptop, KitchenPot, Bath, Bed } from "lucide-react";

interface Room {
  id: string;
  name: string;
  consumption: number;
}

interface RoomEnergyConsumptionProps {
  rooms: Room[];
}

export function RoomEnergyConsumption({ rooms }: RoomEnergyConsumptionProps) {
  const [selectedRoom, setSelectedRoom] = useState<string | null>(null);
  
  // Calculate total energy consumption
  const totalConsumption = rooms.reduce((acc, room) => acc + room.consumption, 0);
  
  // Get max consumption for scaling
  const maxConsumption = Math.max(...rooms.map(room => room.consumption));
  
  // Get appropriate icon for room
  const getRoomIcon = (roomName: string) => {
    const name = roomName.toLowerCase();
    
    if (name.includes("living")) {
      return <LightbulbIcon className="h-5 w-5" />;
    } else if (name.includes("kitchen")) {
      return <KitchenPot className="h-5 w-5" />;
    } else if (name.includes("bedroom")) {
      return <Bed className="h-5 w-5" />;
    } else if (name.includes("bathroom")) {
      return <Bath className="h-5 w-5" />;
    } else if (name.includes("office")) {
      return <Laptop className="h-5 w-5" />;
    } else {
      return <DoorOpen className="h-5 w-5" />;
    }
  };
  
  // Get color intensity based on consumption percentage
  const getColorIntensity = (consumption: number) => {
    const percentage = (consumption / maxConsumption) * 100;
    
    if (percentage > 75) {
      return "bg-red-500";
    } else if (percentage > 50) {
      return "bg-orange-500";
    } else if (percentage > 25) {
      return "bg-yellow-500";
    } else {
      return "bg-green-500";
    }
  };

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-sm font-medium mb-4">Energy by Room</h4>
          <div className="space-y-4">
            {rooms.map((room) => (
              <div
                key={room.id}
                className={`flex items-center space-x-4 p-2 rounded-lg transition-colors ${
                  selectedRoom === room.id ? "bg-blue-50" : ""
                }`}
                onClick={() => setSelectedRoom(room.id === selectedRoom ? null : room.id)}
              >
                <div className="bg-blue-100 p-2 rounded-full text-blue-600">
                  {getRoomIcon(room.name)}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium">{room.name}</span>
                    <span className="text-sm">{room.consumption} kWh</span>
                  </div>
                  <div className="h-2 rounded bg-gray-100 overflow-hidden">
                    <div
                      className={`h-full ${getColorIntensity(room.consumption)}`}
                      style={{
                        width: `${(room.consumption / maxConsumption) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h4 className="text-sm font-medium mb-4">Consumption Breakdown</h4>
          <div className="aspect-square bg-gray-50 rounded-lg p-4 flex items-center justify-center">
            <div className="relative w-full h-full">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <p className="text-lg font-bold text-blue-600">{totalConsumption} kWh</p>
                  <p className="text-xs text-gray-500">Total Energy Usage</p>
                </div>
              </div>
              <svg
                viewBox="0 0 100 100"
                className="w-full h-full"
                style={{ transform: "rotate(-90deg)" }}
              >
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="#f3f4f6"
                  strokeWidth="10"
                />
                {rooms.map((room, index) => {
                  // Calculate percentage of total
                  const percentage = (room.consumption / totalConsumption) * 100;
                  
                  // Calculate previous segments total percentage
                  const previousPercentageTotal = rooms
                    .slice(0, index)
                    .reduce(
                      (acc, r) => acc + (r.consumption / totalConsumption) * 100,
                      0
                    );
                  
                  // Calculate stroke dash array and offset
                  const circumference = 2 * Math.PI * 40;
                  const dashArray = circumference;
                  const dashOffset =
                    circumference - (percentage / 100) * circumference;
                  
                  // Get stroke color
                  const colors = [
                    "stroke-blue-500",
                    "stroke-green-500",
                    "stroke-yellow-500",
                    "stroke-orange-500",
                    "stroke-red-500",
                    "stroke-purple-500",
                    "stroke-indigo-500",
                    "stroke-pink-500",
                  ];
                  
                  return (
                    <circle
                      key={room.id}
                      cx="50"
                      cy="50"
                      r="40"
                      fill="none"
                      className={`${colors[index % colors.length]} ${
                        selectedRoom === room.id ? "stroke-opacity-100" : "stroke-opacity-60"
                      }`}
                      strokeWidth="10"
                      strokeDasharray={dashArray}
                      strokeDashoffset={dashOffset}
                      style={{
                        transformOrigin: "center",
                        transform: `rotate(${previousPercentageTotal * 3.6}deg)`,
                      }}
                    />
                  );
                })}
              </svg>
            </div>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {rooms.map((room, index) => {
              const percentage = (
                (room.consumption / totalConsumption) *
                100
              ).toFixed(1);
              
              // Get color
              const colors = [
                "bg-blue-500",
                "bg-green-500",
                "bg-yellow-500",
                "bg-orange-500",
                "bg-red-500",
                "bg-purple-500",
                "bg-indigo-500",
                "bg-pink-500",
              ];
              
              return (
                <div
                  key={room.id}
                  className={`flex items-center space-x-2 ${
                    selectedRoom === room.id ? "font-medium" : ""
                  }`}
                  onClick={() => setSelectedRoom(room.id === selectedRoom ? null : room.id)}
                >
                  <div
                    className={`w-3 h-3 rounded-full ${colors[index % colors.length]}`}
                  />
                  <span className="text-xs">{room.name}</span>
                  <span className="text-xs text-gray-500 ml-auto">{percentage}%</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
