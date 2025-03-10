import { Home, Lightbulb, Clock, BarChart2, MapPin, Plus, User, Settings } from "lucide-react"
import { NavLink } from "react-router-dom"
import { cn } from "../../lib/utils"

export function NavigationSidebar() {
  return (
    <div className="fixed left-0 top-0 h-screen w-[72px] bg-[#FF9500] flex flex-col items-center py-4 space-y-6">
      <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center">
        <span className="text-[#FF9500] font-bold text-xl">Sy</span>
      </div>
      {[
        { icon: Home, path: "/", exact: true },
        { icon: Lightbulb, path: "/ideas" },
        { icon: Clock, path: "/history" },
        { icon: BarChart2, path: "/analytics" },
        { icon: MapPin, path: "/locations" },
        { icon: Plus, path: "/create" },
        { icon: User, path: "/profile" },
      ].map((item, index) => (
        <NavLink
          key={index}
          to={item.path}
          end={item.exact}
          className={({ isActive }) => cn(
            "w-10 h-10 rounded-xl flex items-center justify-center",
            isActive ? "bg-white" : "hover:bg-white/10"
          )}
        >
          {({ isActive }) => (
            <item.icon className={cn("w-5 h-5", isActive ? "text-[#FF9500]" : "text-white")} />
          )}
        </NavLink>
      ))}
      <div className="mt-auto">
        <NavLink
          to="/settings"
          className={({ isActive }) => cn(
            "w-10 h-10 rounded-xl flex items-center justify-center",
            isActive ? "bg-white" : "hover:bg-white/10"
          )}
        >
          {({ isActive }) => (
            <Settings className={cn("w-5 h-5", isActive ? "text-[#FF9500]" : "text-white")} />
          )}
        </NavLink>
      </div>
    </div>
  )
}
