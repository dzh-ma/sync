// components/family-members.tsx
import { useState, useEffect } from "react";
import { UserPlus, Mail, Clock, AlertCircle, Eye, Lock, Pencil, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "@/components/ui/use-toast";

interface User {
  id: string;
  username: string;
  email: string;
  role?: string;
}

interface AccessDetails {
  id: string;
  owner_id: string;
  user_id: string;
  access_level: string;
  resource_type: string;
  resource_id: string;
  active: boolean;
  created: string;
  updated?: string;
  expires_at?: string;
}

interface FamilyMembersProps {
  userId: string;
  createAuthHeaders: () => Record<string, string>;
  apiUrl: string;
  isDarkMode?: boolean;
}

export function FamilyMembers({ userId, createAuthHeaders, apiUrl, isDarkMode = false }: FamilyMembersProps) {
  const [users, setUsers] = useState<User[]>([]);
  const [accessDetails, setAccessDetails] = useState<AccessDetails[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newUserEmail, setNewUserEmail] = useState("");
  const [newUserAccessLevel, setNewUserAccessLevel] = useState("read");

  // Fetch users and access management details
  useEffect(() => {
    const fetchData = async () => {
      if (!userId) return;

      try {
        setLoading(true);
        
        // Fetch access management entries where current user is the owner
        const accessResponse = await fetch(`${apiUrl}/access-management?owner_id=${userId}`, {
          headers: createAuthHeaders()
        });
        
        if (!accessResponse.ok) {
          throw new Error(`Error fetching access details: ${accessResponse.statusText}`);
        }
        
        const accessData = await accessResponse.json();
        setAccessDetails(accessData);
        
        // Get unique user IDs from access entries
        const uniqueUserIds = [...new Set(accessData.map((entry: AccessDetails) => entry.user_id))];
        
        // Fetch user details for each unique user ID
        const userDetails = await Promise.all(
          uniqueUserIds.map(async (id) => {
            const userResponse = await fetch(`${apiUrl}/users/${id}`, {
              headers: createAuthHeaders()
            });
            
            if (userResponse.ok) {
              return await userResponse.json();
            }
            return null;
          })
        );
        
        // Filter out null results and set users
        setUsers(userDetails.filter(Boolean));
      } catch (error) {
        console.error("Error fetching family members:", error);
        setError("Failed to load family members");
        
        // Set fallback data for preview
        setUsers([
          { id: "1", username: "john.doe", email: "john.doe@example.com" },
          { id: "2", username: "jane.smith", email: "jane.smith@example.com" },
          { id: "3", username: "mike.jones", email: "mike.jones@example.com" }
        ]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [userId, apiUrl, createAuthHeaders]);

  // Add a new family member with access
  const addFamilyMember = async () => {
    try {
      // First, find user by email
      const userResponse = await fetch(`${apiUrl}/users?skip=0&limit=1000`, {
        headers: createAuthHeaders()
      });
      
      if (!userResponse.ok) {
        throw new Error("Failed to search for user");
      }
      
      const allUsers = await userResponse.json();
      const userToAdd = allUsers.find((user: User) => user.email === newUserEmail);
      
      if (!userToAdd) {
        toast({
          title: "User not found",
          description: "No user found with that email address.",
          variant: "destructive"
        });
        return;
      }
      
      // Create access management entry
      const accessResponse = await fetch(`${apiUrl}/access-management`, {
        method: 'POST',
        headers: createAuthHeaders(),
        body: JSON.stringify({
          owner_id: userId,
          resource_id: "home", // Generic resource ID for home access
          resource_type: "home",
          user_ids: [userToAdd.id],
          access_level: newUserAccessLevel
        })
      });
      
      if (!accessResponse.ok) {
        throw new Error("Failed to grant access");
      }
      
      const newAccessEntries = await accessResponse.json();
      
      // Update local state
      setAccessDetails([...accessDetails, ...newAccessEntries]);
      setUsers([...users, userToAdd]);
      
      // Reset and close dialog
      setNewUserEmail("");
      setNewUserAccessLevel("read");
      setIsAddDialogOpen(false);
      
      toast({
        title: "Family member added",
        description: `${userToAdd.username} has been granted ${newUserAccessLevel} access.`
      });
    } catch (error) {
      console.error("Error adding family member:", error);
      toast({
        title: "Error",
        description: "Failed to add family member.",
        variant: "destructive"
      });
    }
  };

  // Update access level for a user
  const updateAccessLevel = async (userId: string, newLevel: string) => {
    try {
      // Find the access entry for this user
      const accessEntry = accessDetails.find(entry => entry.user_id === userId);
      
      if (!accessEntry) {
        throw new Error("Access entry not found");
      }
      
      // Update the access level
      const response = await fetch(`${apiUrl}/access-management/${accessEntry.id}`, {
        method: 'PATCH',
        headers: createAuthHeaders(),
        body: JSON.stringify({
          access_level: newLevel
        })
      });
      
      if (!response.ok) {
        throw new Error("Failed to update access level");
      }
      
      // Update local state
      setAccessDetails(accessDetails.map(entry => 
        entry.id === accessEntry.id 
          ? {...entry, access_level: newLevel} 
          : entry
      ));
      
      toast({
        title: "Access updated",
        description: `Access level updated to ${newLevel}.`
      });
    } catch (error) {
      console.error("Error updating access:", error);
      toast({
        title: "Error",
        description: "Failed to update access level.",
        variant: "destructive"
      });
    }
  };

  // Remove access for a user
  const removeFamilyMember = async (userId: string) => {
    try {
      // Find all access entries for this user
      const entriesToRemove = accessDetails.filter(entry => entry.user_id === userId);
      
      if (entriesToRemove.length === 0) {
        throw new Error("Access entries not found");
      }
      
      // Delete each entry
      await Promise.all(
        entriesToRemove.map(async (entry) => {
          const response = await fetch(`${apiUrl}/access-management/${entry.id}`, {
            method: 'DELETE',
            headers: createAuthHeaders()
          });
          
          if (!response.ok) {
            throw new Error(`Failed to delete access entry ${entry.id}`);
          }
        })
      );
      
      // Update local state
      setAccessDetails(accessDetails.filter(entry => !entriesToRemove.includes(entry)));
      setUsers(users.filter(user => user.id !== userId));
      
      toast({
        title: "Family member removed",
        description: "Access has been revoked."
      });
    } catch (error) {
      console.error("Error removing family member:", error);
      toast({
        title: "Error",
        description: "Failed to remove family member.",
        variant: "destructive"
      });
    }
  };

  // Get access level for a user
  const getUserAccessLevel = (userId: string): string => {
    const entry = accessDetails.find(a => a.user_id === userId);
    return entry?.access_level || "unknown";
  };

  // Get badge color based on access level
  const getAccessLevelBadge = (level: string) => {
    switch (level) {
      case "manage":
        return <Badge className="bg-blue-500">Manage</Badge>;
      case "control":
        return <Badge className="bg-green-500">Control</Badge>;
      case "read":
        return <Badge className="bg-yellow-500">View Only</Badge>;
      default:
        return <Badge className="bg-gray-500">Unknown</Badge>;
    }
  };

  // Get access level icon
  const getAccessLevelIcon = (level: string) => {
    switch (level) {
      case "manage":
        return <Pencil className="h-4 w-4" />;
      case "control":
        return <Lock className="h-4 w-4" />;
      case "read":
        return <Eye className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-sm font-medium">Family Members</h3>
        </div>
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center space-x-4">
              <div className="rounded-full bg-gray-200 h-10 w-10"></div>
              <div className="flex-1">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2 mt-2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-sm font-medium">Family Members</h3>
        </div>
        <div className={`p-4 rounded-md ${isDarkMode ? 'bg-red-900/20' : 'bg-red-50'} text-red-500`}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-medium">Family Members</h3>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <UserPlus className="h-4 w-4" />
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Family Member</DialogTitle>
              <DialogDescription>
                Grant access to your smart home for a family member.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <label htmlFor="email" className="text-sm">
                  Email Address
                </label>
                <div className="flex items-center">
                  <Mail className="mr-2 h-4 w-4 text-gray-500" />
                  <Input
                    id="email"
                    value={newUserEmail}
                    onChange={(e) => setNewUserEmail(e.target.value)}
                    placeholder="user@example.com"
                    className="col-span-3"
                  />
                </div>
              </div>
              <div className="grid gap-2">
                <label htmlFor="access" className="text-sm">
                  Access Level
                </label>
                <Select
                  value={newUserAccessLevel}
                  onValueChange={setNewUserAccessLevel}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select access level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="read">View Only</SelectItem>
                    <SelectItem value="control">Control Devices</SelectItem>
                    <SelectItem value="manage">Full Management</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={addFamilyMember}>Add Member</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      {users.length === 0 ? (
        <div className={`p-6 rounded-md ${isDarkMode ? 'bg-gray-800' : 'bg-gray-100'} text-center`}>
          <UserRound className="h-10 w-10 mx-auto text-gray-400 mb-2" />
          <h3 className="text-sm font-medium mb-1">No family members yet</h3>
          <p className="text-xs text-gray-500 mb-4">
            Add family members to share your smart home.
          </p>
          <Button variant="default" size="sm" onClick={() => setIsAddDialogOpen(true)}>
            <UserPlus className="mr-2 h-4 w-4" />
            Add Family Member
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          {users.map((user) => {
            const accessLevel = getUserAccessLevel(user.id);
            return (
              <div
                key={user.id}
                className={`p-3 rounded-lg ${
                  isDarkMode ? "bg-gray-800" : "bg-gray-50"
                }`}
              >
                <div className="flex items-center space-x-3 mb-2">
                  <Avatar>
                    <AvatarFallback>
                      {user.username.substring(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="flex items-center">
                      <h4 className="text-sm font-medium">{user.username}</h4>
                      <span className="ml-2">
                        {getAccessLevelBadge(accessLevel)}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">{user.email}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center text-xs text-gray-500">
                    <Clock className="h-3 w-3 mr-1" />
                    <span>Added {getRelativeTimeString(accessDetails.find(a => a.user_id === user.id)?.created || "")}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Select
                      defaultValue={accessLevel}
                      onValueChange={(value) => updateAccessLevel(user.id, value)}
                    >
                      <SelectTrigger className="h-7 w-auto min-w-[110px] text-xs">
                        <div className="flex items-center">
                          {getAccessLevelIcon(accessLevel)}
                          <span className="ml-1">
                            {accessLevel.charAt(0).toUpperCase() + accessLevel.slice(1)}
                          </span>
                        </div>
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="read">View Only</SelectItem>
                        <SelectItem value="control">Control</SelectItem>
                        <SelectItem value="manage">Manage</SelectItem>
                      </SelectContent>
                    </Select>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-7 w-7"
                      onClick={() => removeFamilyMember(user.id)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// Helper function to format relative time strings
function getRelativeTimeString(dateString: string): string {
  if (!dateString) return "recently";
  
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays < 1) {
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    if (diffHours < 1) {
      const diffMinutes = Math.floor(diffMs / (1000 * 60));
      return diffMinutes < 1 ? "just now" : `${diffMinutes}m ago`;
    }
    return `${diffHours}h ago`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else if (diffDays < 30) {
    const diffWeeks = Math.floor(diffDays / 7);
    return `${diffWeeks}w ago`;
  } else {
    const diffMonths = Math.floor(diffDays / 30);
    return `${diffMonths}mo ago`;
  }
}
