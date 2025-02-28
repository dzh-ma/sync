import { Switch } from "@/components/ui/switch"
import { Wind } from "lucide-react"

export function AirConditionerControl() {
  return (
    <div className="p-4 bg-white rounded-xl">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h3 className="font-medium">Air Conditioner</h3>
          <p className="text-sm text-muted-foreground">LG Smart Inverter</p>
        </div>
        <Switch />
      </div>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <span>16°C</span>
          <span className="text-3xl font-bold text-[#00B2FF]">20°C</span>
          <span>30°C</span>
        </div>
        <div className="flex space-x-2">
          <div className="flex-1 bg-[#00B2FF] rounded-xl p-3 text-white">
            <Wind className="w-5 h-5 mb-1" />
            <span className="text-sm">III</span>
          </div>
          <div className="flex-1 bg-gray-100 rounded-xl p-3">
            <span className="text-sm font-medium">AUTO</span>
          </div>
          <div className="flex-1 bg-gray-100 rounded-xl p-3">
            <span className="text-sm">↔</span>
          </div>
        </div>
      </div>
    </div>
  )
}

