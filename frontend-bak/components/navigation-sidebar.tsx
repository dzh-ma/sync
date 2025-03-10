import { Home, Lightbulb, Clock, BarChart2, MapPin, Plus, User, Settings } from "lucide-react"
import { cn } from "../lib/utils"

export function NavigationSidebar() {
  return (
    <div className="fixed left-0 top-0 h-screen w-[72px] bg-[#FF9500] flex flex-col items-center py-4 space-y-6">
      <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center">
        <span className="text-[#FF9500] font-bold text-xl">Sy</span>
      </div>
      {[
        { icon: Home, active: true },
        { icon: Lightbulb },
        { icon: Clock },
        { icon: BarChart2 },
        { icon: MapPin },
        { icon: Plus },
        { icon: User },
      ].map((item, index) => (
        <button
          key={index}
          className={cn(
            "w-10 h-10 rounded-xl flex items-center justify-center",
            item.active ? "bg-white" : "hover:bg-white/10",
          )}
        >
          <item.icon className={cn("w-5 h-5", item.active ? "text-[#FF9500]" : "text-white")} />
        </button>
      ))}
      <div className="mt-auto">
        <button className="w-10 h-10 rounded-xl flex items-center justify-center hover:bg-white/10">
          <Settings className="w-5 h-5 text-white" />
        </button>
      </div>
    </div>
  )
}

