"use client"

import { useState } from "react"
import { Home, Lightbulb, Clock, BarChart2, Plus, User, Settings, Smartphone } from "lucide-react"
import { cn } from "@/lib/utils"
import { usePathname, useRouter } from "next/navigation"
import Link from "next/link"
import { AccessDeniedDialog } from "@/components/access-denied-dialog"

const navigationItems = [
  { icon: Home, path: "/", label: "Dashboard" },
  { icon: Lightbulb, path: "/suggestions", label: "Suggestions" },
  { icon: Clock, path: "/automations", label: "Automations", requiredPermission: "addAutomation" },
  { icon: BarChart2, path: "/statistics", label: "Statistics", requiredPermission: "statisticalData" },
  { icon: Smartphone, path: "/devices", label: "Devices" },
  { icon: Plus, path: "/add-room", label: "Add Room" },
  { icon: User, path: "/profile", label: "Profile" },
  { icon: Settings, path: "/settings", label: "Settings" },
]

export function NavigationSidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const [accessDeniedOpen, setAccessDeniedOpen] = useState(false)
  const [deniedFeature, setDeniedFeature] = useState("")

  const handleNavigation = (path: string, requiredPermission?: string) => {
    // TODO: Add user role restricted access
    router.push(path)
  }

  return (
    <>
      <div className="fixed left-0 top-0 h-screen w-[72px] bg-[#FF9500] flex flex-col items-center py-4 space-y-6">
        <Link href="/">
          <div className="w-[52px] h-[32px] bg-gradient-to-r from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-sm">
              Sy<span className="text-[#FFB800]">nc</span>
            </span>
          </div>
        </Link>
        {navigationItems.map((item) => (
          <button
            key={item.path}
            onClick={() => handleNavigation(item.path, item.requiredPermission)}
            className={cn(
              "w-10 h-10 rounded-xl flex items-center justify-center",
              pathname === item.path ? "bg-white" : "hover:bg-white/10",
            )}
          >
            <item.icon className={cn("w-5 h-5", pathname === item.path ? "text-[#FF9500]" : "text-white")} />
          </button>
        ))}
      </div>
      <AccessDeniedDialog
        isOpen={accessDeniedOpen}
        onClose={() => setAccessDeniedOpen(false)}
        featureName={deniedFeature}
      />
    </>
  )
}

