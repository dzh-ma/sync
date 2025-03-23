"use client"

import { useState, useEffect } from "react"
import { Home, Lightbulb, Clock, BarChart2, Plus, User, Settings, Smartphone, LogOut } from "lucide-react"
import { cn } from "@/lib/utils"
import { usePathname, useRouter } from "next/navigation"
import Link from "next/link"
import { AccessDeniedDialog } from "@/components/access-denied-dialog"
import { useToast } from "@/components/ui/use-toast"

const navigationItems = [
  { icon: Home, path: "/dashboard", label: "Dashboard" },
  { icon: Lightbulb, path: "/suggestions", label: "Suggestions" },
  { icon: Clock, path: "/automations", label: "Automations", requiredPermission: "addAutomation" },
  { icon: BarChart2, path: "/statistics", label: "Statistics", requiredPermission: "statisticalData" },
  { icon: Smartphone, path: "/devices", label: "Devices", requiredPermission: "deviceControl" },
  { icon: Plus, path: "/add-room", label: "Add Room", requiredPermission: "roomControl" },
  { icon: User, path: "/profile", label: "Profile" },
  { icon: Settings, path: "/settings", label: "Settings" },
  { icon: LogOut, path: "/logout", label: "Logout" },
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
        
        if (storedUser) {
          const currentUser = JSON.parse(storedUser);
          setUserType("admin");
          
          // Make sure we're getting permissions correctly
          if (currentUser && currentUser.permissions) {
            console.log("Admin user permissions:", currentUser.permissions);
            setUserPermissions(currentUser.permissions);
            
            // Force all permissions to be true for admin users
            const allPermissions = {
              notifications: true,
              energyAlerts: true,
              addAutomation: true,
              statisticalData: true,
              deviceControl: true,
              roomControl: true,
            };
            
            // Update the user with all permissions
            const updatedUser = {
              ...currentUser,
              permissions: allPermissions
            };
            
            // Save the updated user back to localStorage
            localStorage.setItem("currentUser", JSON.stringify(updatedUser));
            setUserPermissions(allPermissions);
          } else {
            console.warn("User found but no permissions object:", currentUser);
            
            // Create default permissions for admin
            const defaultPermissions = {
              notifications: true,
              energyAlerts: true,
              addAutomation: true,
              statisticalData: true,
              deviceControl: true,
              roomControl: true,
            };
            
            // Update user with default permissions
            const updatedUser = {
              ...currentUser,
              permissions: defaultPermissions
            };
            
            localStorage.setItem("currentUser", JSON.stringify(updatedUser));
            setUserPermissions(defaultPermissions);
          }
        } else if (storedMember) {
          const currentMember = JSON.parse(storedMember);
          setUserType("member");
          
          // Make sure we're getting permissions correctly from the member object
          if (currentMember && currentMember.permissions) {
            console.log("Member user permissions:", currentMember.permissions);
            setUserPermissions(currentMember.permissions);
          } else {
            console.warn("Member found but no permissions object:", currentMember);
            
            // Create default permissions for members
            const defaultPermissions = {
              notifications: true,
              energyAlerts: true,
              deviceControl: true,
              roomControl: false,
              addAutomation: false,
              statisticalData: true,
            };
            
            // Update member with default permissions
            const updatedMember = {
              ...currentMember,
              permissions: defaultPermissions
            };
            
            localStorage.setItem("currentMember", JSON.stringify(updatedMember));
            setUserPermissions(defaultPermissions);
          }
        } else {
          console.warn("No user or member found in localStorage");
        }
      } catch (error) {
        console.error("Error loading user permissions:", error);
      }
    }
  }, [toast]);

  const handleNavigation = (path: string, requiredPermission?: string) => {
    if (path === "/logout") {
      // Handle logout
      localStorage.removeItem("currentUser");
      localStorage.removeItem("currentMember");
      router.push("/auth/login");
      return;
    }
    
    // Check if this path requires a permission
    if (requiredPermission) {
      console.log(`Checking permission for ${path}: ${requiredPermission}`);
      console.log("User permissions:", userPermissions);
      
      // For the statistics page, allow access regardless of permission
      if (path === "/statistics") {
        console.log("Granting access to statistics page");
        router.push(path);
        return;
      }
      
      // Check if user has permission
      if (!userPermissions[requiredPermission]) {
        console.log(`Permission denied: ${requiredPermission}`);
        setDeniedFeature(navigationItems.find((item) => item.path === path)?.label || "");
        setAccessDeniedOpen(true);
        return;
      }
    }
    
    // If no permission required or user has permission, navigate
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

