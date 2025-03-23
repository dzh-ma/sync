import { Battery, Zap } from "lucide-react"

export function EnergyConsumption() {
  return (
    <div className="bg-white rounded-xl p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-medium">Energy Consumed</h3>
        <span className="text-sm text-muted-foreground">Summary of today's consumption</span>
      </div>
      <div className="flex items-center space-x-2 mb-4">
        <Zap className="w-6 h-6 text-[#00B2FF]" />
        <span className="text-2xl font-bold">34</span>
        <span className="text-sm text-muted-foreground">kWh</span>
        <span className="text-sm ml-auto text-[#00B2FF]">View Analytics</span>
      </div>
      <div className="space-y-2">
        {[
          { room: "Living room", value: 7, status: "Low" },
          { room: "Kitchen", value: 10, status: "Medium" },
          { room: "Main Bedroom", value: 5, status: "High" },
        ].map((item) => (
          <div key={item.room} className="flex items-center">
            <Battery className="w-4 h-4 mr-2" />
            <span className="text-sm flex-1">{item.room}</span>
            <span className="text-sm font-medium">{item.value}</span>
            <div
              className={`ml-2 px-2 py-0.5 rounded text-xs ${
                item.status === "Low"
                  ? "bg-green-100 text-green-700"
                  : item.status === "Medium"
                    ? "bg-yellow-100 text-yellow-700"
                    : "bg-red-100 text-red-700"
              }`}
            >
              {item.status}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

