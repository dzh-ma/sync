"use client";

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { 
  Home, 
  Settings, 
  Users, 
  Zap, 
  LogOut, 
  ChevronRight, 
  ChevronLeft, 
  BarChart, 
  PieChart,
  Thermometer,
  Door
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useUser } from "@/contexts/UserContext";

export function NavigationSidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const { logout } = useUser();
  const [expanded, setExpanded] = useState(false);

  const navItems = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: Home,
    },
    {
      name: "Rooms",
      href: "/rooms",
      icon: Door,
    },
    {
      name: "Devices",
      href: "/devices",
      icon: Thermometer,
    },
    {
      name: "Automations",
      href: "/automations",
      icon: Zap,
    },
    {
      name: "Family",
      href: "/family",
      icon: Users,
    },
    {
      name: "Energy",
      href: "/energy",
      icon: BarChart,
    },
    {
      name: "Analytics",
      href: "/analytics",
      icon: PieChart,
    },
    {
      name: "Settings",
      href: "/settings",
      icon: Settings,
    },
  ];

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <div
      className={cn(
        "fixed left-0 top-0 bottom-0 z-40 flex flex-col transition-all duration-300 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800",
        expanded ? "w-64" : "w-16"
      )}
    >
      <div className="flex items-center justify-between p-4">
        {expanded && (
          <div className="flex items-center">
            <div className="w-8 h-8 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-sm">Sy</span>
            </div>
            <span className="ml-2 font-semibold">Sync</span>
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setExpanded(!expanded)}
          className="ml-auto"
        >
          {expanded ? (
            <ChevronLeft className="h-5 w-5" />
          ) : (
            <ChevronRight className="h-5 w-5" />
          )}
        </Button>
      </div>

      <nav className="flex flex-col flex-1 gap-2 p-2">
        <TooltipProvider>
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Tooltip key={item.href} delayDuration={expanded ? 999999 : 300}>
                <TooltipTrigger asChild>
                  <Link
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 rounded-md",
                      isActive
                        ? "bg-gray-100 dark:bg-gray-800 text-blue-600 dark:text-blue-400"
                        : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                    )}
                  >
                    <item.icon className="h-5 w-5 flex-shrink-0" />
                    {expanded && <span>{item.name}</span>}
                  </Link>
                </TooltipTrigger>
                {!expanded && (
                  <TooltipContent side="right">
                    <span>{item.name}</span>
                  </TooltipContent>
                )}
              </Tooltip>
            );
          })}
        </TooltipProvider>
      </nav>

      <div className="p-2">
        <TooltipProvider>
          <Tooltip delayDuration={expanded ? 999999 : 300}>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                className="w-full flex items-center justify-start gap-3 px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800"
                onClick={handleLogout}
              >
                <LogOut className="h-5 w-5 flex-shrink-0" />
                {expanded && <span>Log out</span>}
              </Button>
            </TooltipTrigger>
            {!expanded && (
              <TooltipContent side="right">
                <span>Log out</span>
              </TooltipContent>
            )}
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>
  );
}
