"use client"

import { useState, useEffect } from "react"
import { Home, Lightbulb, Clock, BarChart2, Plus, User, Settings, Smartphone, LogOut } from "lucide-react"
import { cn } from "@/lib/utils"
import { usePathname, useRouter } from "next/navigation"
import Link from "next/link"
import { AccessDeniedDialog } from "@/components/access-denied-dialog"
import { useToast } from "@/components/ui/use-toast"
import { NavigationTooltip } from "./navigation-tooltip"

const navigationItems = [
  { 
    icon: Home, 
    path: "/dashboard", 
    label: "Dashboard",
    description: "Main overview of your smart home"
  },
  { 
    icon: Lightbulb, 
    path: "/suggestions", 
    label: "Suggestions",
    description: "Energy-saving tips and recommendations"
  },
  { 
    icon: Clock, 
    path: "/automations", 
    label: "Automations", 
    requiredPermission: "addAutomation",
    description: "Set up and manage automated routines"
  },
  { 
    icon: BarChart2, 
    path: "/statistics", 
    label: "Statistics", 
    requiredPermission: "statisticalData",
    description: "View energy consumption analytics"
  },
  { 
    icon: Smartphone, 
    path: "/devices", 
    label: "Devices", 
    requiredPermission: "deviceControl",
    description: "Manage your connected devices"
  },
  { 
    icon: Plus, 
    path: "/add-room", 
    label: "Add Room", 
    requiredPermission: "roomControl",
    description: "Add and configure new rooms"
  },
  { 
    icon: User, 
    path: "/profile", 
    label: "Profile",
    description: "View and edit your user profile"
  },
  { 
    icon: Settings, 
    path: "/settings", 
    label: "Settings",
    description: "Configure app preferences"
  },
  { 
    icon: LogOut, 
    path: "/logout", 
    label: "Logout",
    description: "Sign out of your account"
  },
]

export function NavigationSidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const [accessDeniedOpen, setAccessDeniedOpen] = useState(false)
  const [deniedFeature, setDeniedFeature] = useState("")
  const [userType, setUserType] = useState<"admin" | "member" | null>(null)
  const [userPermissions, setUserPermissions] = useState<Record<string, boolean>>({})
  const [mounted, setMounted] = useState(false)
  const { toast } = useToast()

  // Load user permissions
  useEffect(() => {
    // Mark component as mounted (client-side only)
    setMounted(true)
    
    // Only run this code on the client side
    if (typeof window !== 'undefined') {
      try {
        // Check for both currentUser (admin) and currentMember (household member)
        const storedUser = localStorage.getItem("currentUser");
        const storedMember = localStorage.getItem("currentMember");
        
        // Clear permission state if nothing in localStorage (e.g., after logout)
        if (!storedUser && !storedMember) {
          setUserType(null);
          setUserPermissions({});
          return;
        }
        
        if (storedUser) {
          const currentUser = JSON.parse(storedUser);
          setUserType("admin");
          
          // Admin has full permissions by default
          const adminDefaultPermissions = {
            notifications: true,
            energyAlerts: true,
            addAutomation: true,
            statisticalData: true,
            deviceControl: true,
            roomControl: true
          };
          
          // If admin has specific permissions, use those
          if (currentUser && currentUser.permissions) {
            console.log("Admin user permissions:", currentUser.permissions);
            setUserPermissions(currentUser.permissions);
          } else {
            // Set full permissions for admin
            console.log("Setting default admin permissions");
            setUserPermissions(adminDefaultPermissions);
          }
        } else if (storedMember) {
          const currentMember = JSON.parse(storedMember);
          setUserType("member");
          
          // Make sure we're getting permissions correctly from the member object
          if (currentMember && currentMember.permissions) {
            // Log for debugging
            console.log("Member user permissions from localStorage:", currentMember.permissions);
            
            // Always use the permissions from localStorage which should be updated by the backend
            setUserPermissions(currentMember.permissions);
          } else {
            console.warn("Member found but no permissions object:", currentMember);
            // Create empty permissions object - don't assume any permissions
            setUserPermissions({});
            
            // If the member has an ID and a household ID, try to fetch latest permissions from API
            if (currentMember.id && currentMember.householdId) {
              const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
              console.log("Fetching latest permissions for member:", currentMember.id);
              
              // Perform the fetch in an async IIFE
              (async () => {
                try {
                  const response = await fetch(`${API_URL}/api/permissions/${currentMember.id}`);
                  if (response.ok) {
                    const permissionsData = await response.json();
                    console.log("Fetched latest permissions:", permissionsData);
                    
                    // Update permissions in state
                    setUserPermissions(permissionsData);
                    
                    // Update the member object in localStorage with latest permissions
                    const updatedMember = {
                      ...currentMember,
                      permissions: permissionsData
                    };
                    localStorage.setItem("currentMember", JSON.stringify(updatedMember));
                    console.log("Updated member in localStorage with latest permissions");
                  } else {
                    console.error("Failed to fetch permissions:", await response.text());
                  }
                } catch (error) {
                  console.error("Error fetching permissions:", error);
                }
              })();
            }
          }
        }
      } catch (error) {
        console.error("Error loading user permissions:", error);
        // Reset permissions on error
        setUserPermissions({});
      }
    }
  }, [pathname]); // Re-run when pathname changes, which will happen after navigation including logout/login

  const handleNavigation = (path: string, requiredPermission?: string) => {
    if (path === "/logout") {
      // Handle logout
      console.log("Logging out and clearing user data");
      localStorage.removeItem("currentUser");
      localStorage.removeItem("currentMember");
      // Set fresh login flag for proper data reload
      localStorage.setItem("freshLogin", "true");
      // Reset permissions state immediately
      setUserType(null);
      setUserPermissions({});
      // Navigate to login
      router.push("/auth/login");
      return;
    }
    
    // These pages are always accessible to all users
    const alwaysAccessiblePaths = ["/dashboard", "/profile", "/suggestions"];
    if (alwaysAccessiblePaths.includes(path)) {
      router.push(path);
      return;
    }
    
    // Admin can access all pages
    if (userType === "admin") {
      router.push(path);
      return;
    }
    
    // For household members, check permissions for protected pages
    if (userType === "member" && requiredPermission) {
      console.log(`Checking permission for ${path}: ${requiredPermission}`);
      console.log("Current user permissions:", userPermissions);
      
      // Get the most recent permissions directly from localStorage
      try {
        const storedMember = localStorage.getItem("currentMember");
        if (storedMember) {
          const freshPermissions = JSON.parse(storedMember).permissions;
          console.log("Fresh permissions from localStorage:", freshPermissions);
          
          // Use the most recent permissions from localStorage
          if (freshPermissions && !freshPermissions[requiredPermission]) {
            console.log(`Permission denied using fresh permissions: ${requiredPermission}`);
            setDeniedFeature(navigationItems.find((item) => item.path === path)?.label || "");
            setAccessDeniedOpen(true);
            return;
          }
        }
      } catch (e) {
        console.error("Error checking fresh permissions:", e);
      }
      
      // Check if user has the required permission (using state as fallback)
      if (!userPermissions[requiredPermission]) {
        console.log(`Permission denied using state permissions: ${requiredPermission}`);
        setDeniedFeature(navigationItems.find((item) => item.path === path)?.label || "");
        setAccessDeniedOpen(true);
        return;
      }
    }
    
    // If we reached here, navigation is allowed
    router.push(path);
  }

  return (
    <>
      <div className="fixed left-0 top-0 h-screen w-[72px] bg-[#FF9500] flex flex-col items-center py-4 space-y-6">
        <Link href="/dashboard">
          <div className="w-[52px] h-[32px] bg-gradient-to-r from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-sm">
              Sy<span className="text-[#FFB800]">nc</span>
            </span>
          </div>
        </Link>
        {navigationItems.map((item) => (
          <NavigationTooltip
            key={item.path}
            label={item.label}
            description={item.description}
          >
            <button
              onClick={() => handleNavigation(item.path, item.requiredPermission)}
              className={cn(
                "w-10 h-10 rounded-xl flex items-center justify-center",
                pathname === item.path ? "bg-white" : "hover:bg-white/10",
              )}
            >
              <item.icon className={cn("w-5 h-5", pathname === item.path ? "text-[#FF9500]" : "text-white")} />
            </button>
          </NavigationTooltip>
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

