"use client";

import { useState, useEffect } from "react";
import { Loader2, UserPlus, Users, User, Shield, UserCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/components/ui/use-toast";
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
import { Input } from "@/components/ui/input";

interface AccessManagement {
  id: string;
  owner_id: string;
  resource_id: string;
  resource_type: string;
  user_id: string;
  access_level: string;
  active: boolean;
  created: string;
}

interface User {
  id: string;
  username: string;
  active: boolean;
}

interface FamilyMembersProps {
  userId?: string;
  token?: string;
  apiUrl?: string;
}

export function FamilyMembers({ userId, token, apiUrl = 'http://localhost:8000/api/v1' }: FamilyMembersProps) {
  const [accessEntries, setAccessEntries] = useState<AccessManagement[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [newMemberEmail, setNewMemberEmail] = useState("");
  const [selectedAccessLevel, setSelectedAccessLevel] = useState("read");
  const [selectedResource, setSelectedResource] = useState("");
  const [resources, setResources] = useState<{id: string, name: string, type: string}[]>([]);

  useEffect(() => {
    const fetchAccessData = async () => {
      if (!userId || !token) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        
        // Fetch access management entries where current user is the owner
        const accessResponse = await fetch(`${apiUrl}/access-management?owner_id=${userId}`, {
          headers: {
            'Authorization': `Basic ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!accessResponse.ok) {
          throw new Error(`Error fetching access data: ${accessResponse.status}`);
        }

        const accessData = await accessResponse.json();
        setAccessEntries(accessData);
        
        // Extract unique user IDs
        const userIds = [...new Set(accessData.map((entry: AccessManagement) => entry.user_id))];
        
        // Fetch user data for each user ID (in a real app, you'd do this in a batch)
        const userPromises = userIds.map(async (id) => {
          try {
            const userResponse = await fetch(`${apiUrl}/users/${id}`, {
              headers: {
                'Authorization': `Basic ${token}`,
                'Content-Type': 'application/json'
              }
            });
            
            if (userResponse.ok) {
              return await userResponse.json();
            }
            return null;
          } catch (error) {
            console.error(`Failed to fetch user ${id}:`, error);
            return null;
          }
        });
        
        const userData = await Promise.all(userPromises);
        setUsers(userData.filter(user => user !== null));
        
        // Fetch resources (homes, rooms, devices) for sharing
        // This would be more complex in a real app
        const devicesResponse = await fetch(`${apiUrl}/devices?user_id=${userId}`, {
          headers: {
            'Authorization': `Basic ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        const roomsResponse = await fetch(`${apiUrl}/rooms?user_id=${userId}`, {
          headers: {
            'Authorization': `Basic ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        let deviceResources: any[] = [];
        let roomResources: any[] = [];
        
        if (devicesResponse.ok) {
          const devicesData = await devicesResponse.json();
          deviceResources = devicesData.map((device: any) => ({
            id: device.id,
            name: device.name,
            type: 'device'
          }));
        }
        
        if (roomsResponse.ok) {
          const roomsData = await roomsResponse.json();
          roomResources = roomsData.map((room: any) => ({
            id: room.id,
            name: room.name,
            type: 'room'
          }));
        }
        
        setResources([...deviceResources, ...roomResources]);
        
      } catch (err) {
        console.error("Failed to fetch access data:", err);
        
        // Set fallback data for development
        setAccessEntries([
          { 
            id: "1", 
            owner_id: userId || "owner1", 
            resource_id: "resource1", 
            resource_type: "DEVICE", 
            user_id: "user1",
            access_level: "READ",
            active: true,
            created: new Date().toISOString()
          },
          { 
            id: "2", 
            owner_id: userId || "owner1", 
            resource_id: "resource2", 
            resource_type: "ROOM", 
            user_id: "user2",
            access_level: "CONTROL",
            active: true,
            created: new Date().toISOString()
          }
        ]);
        
        setUsers([
          { id: "user1", username: "family.member1", active: true },
          { id: "user2", username: "family.member2", active: true }
        ]);
        
        setResources([
          { id: "resource1", name: "Living Room Lights", type: "device" },
          { id: "resource2", name: "Kitchen", type: "room" }
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAccessData();
  }, [userId, token, apiUrl]);

  const handleAddMember = async () => {
    if (!userId || !token || !newMemberEmail || !selectedAccessLevel || !selectedResource) {
      toast({
        title: "Error",
        description: "Please fill out all fields",
        variant: "destructive"
      });
      return;
    }

    try {
      // In a real app, you'd first search for the user by email
      // For this example, we'll create a mock user ID
      const mockUserId = `user-${Date.now()}`;
      
      const selectedResourceObj = resources.find(r => r.id === selectedResource);
      
      // Create access management entry
      const response = await fetch(`${apiUrl}/access-management`, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          owner_id: userId,
          resource_id: selectedResource,
          resource_type: selectedResourceObj?.type.toUpperCase() || "DEVICE",
          user_ids: [mockUserId],
          access_level: selectedAccessLevel.toUpperCase()
        })
      });

      if (!response.ok) {
        throw new Error(`Error creating access: ${response.status}`);
      }

      const data = await response.json();
      
      // Update state with new access entry
      setAccessEntries(prev => [...prev, ...data]);
      
      // Add mock user data (in a real app, you'd get this from the API)
      setUsers(prev => [...prev, { 
        id: mockUserId, 
        username: newMemberEmail.split('@')[0], 
        active: true 
      }]);
      
      toast({
        title: "Member Added",
        description: `${newMemberEmail} has been granted access.`,
      });
      
      // Reset form
      setNewMemberEmail("");
      setSelectedAccessLevel("read");
      setSelectedResource("");
      setIsAddDialogOpen(false);
      
    } catch (err) {
      console.error("Failed to add member:", err);
      
      toast({
        title: "Error",
        description: "Failed to add member. Please try again.",
        variant: "destructive"
      });
    }
  };

  const handleRemoveAccess = async (accessId: string) => {
    if (!userId || !token) return;
    
    try {
      // Update optimistically
      setAccessEntries(prev => prev.filter(entry => entry.id !== accessId));
      
      // Send deletion request to API
      const response = await fetch(`${apiUrl}/access-management/${accessId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Basic ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`Error removing access: ${response.status}`);
      }
      
      toast({
        title: "Access Removed",
        description: "Access has been removed successfully.",
      });
      
    } catch (err) {
      console.error("Failed to remove access:", err);
      
      // Refetch to restore correct state
      const accessResponse = await fetch(`${apiUrl}/access-management?owner_id=${userId}`, {
        headers: {
          'Authorization': `Basic ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (accessResponse.ok) {
        const accessData = await accessResponse.json();
        setAccessEntries(accessData);
      }
      
      toast({
        title: "Error",
        description: "Failed to remove access. Please try again.",
        variant: "destructive"
      });
    }
  };

  const getAccessLevelIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case "admin":
        return <Shield className="w-4 h-4 text-red-500" />;
      case "manage":
        return <UserCheck className="w-4 h-4 text-purple-500" />;
      case "control":
        return <User className="w-4 h-4 text-blue-500" />;
      case "read":
      default:
        return <User className="w-4 h-4 text-gray-500" />;
    }
  };

  const getAccessLevelBadge = (level: string) => {
    let color = "";
    switch (level.toLowerCase()) {
      case "admin":
        color = "bg-red-100 text-red-800";
        break;
      case "manage":
        color = "bg-purple-100 text-purple-800";
        break;
      case "control":
        color = "bg-blue-100 text-blue-800";
        break;
      case "read":
      default:
        color = "bg-gray-100 text-gray-800";
    }
    
    return (
      <Badge variant="outline" className={`${color} text-xs`}>
        {level}
      </Badge>
    );
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-4">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500 mb-2" />
        <p className="text-sm text-gray-500">Loading access data...</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium flex items-center">
          <Users className="w-5 h-5 mr-2 text-blue-500" />
          Shared Access
        </h3>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm">
              <UserPlus className="w-4 h-4 mr-1" /> Add
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add Family Member</DialogTitle>
              <DialogDescription>
                Grant access to your smart home devices and rooms.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">Email Address</label>
                <Input 
                  placeholder="email@example.com" 
                  value={newMemberEmail}
                  onChange={(e) => setNewMemberEmail(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Access Level</label>
                <Select value={selectedAccessLevel} onValueChange={setSelectedAccessLevel}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select access level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="read">Read Only</SelectItem>
                    <SelectItem value="control">Control</SelectItem>
                    <SelectItem value="manage">Manage</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Resource</label>
                <Select value={selectedResource} onValueChange={setSelectedResource}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select resource" />
                  </SelectTrigger>
                  <SelectContent>
                    {resources.map((resource) => (
                      <SelectItem key={resource.id} value={resource.id}>
                        {resource.name} ({resource.type})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddMember}>Add Member</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      
      {accessEntries.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-6 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <Users className="w-10 h-10 text-gray-400 mb-2" />
          <p className="text-sm text-gray-500 text-center">
            No family members have access to your smart home yet
          </p>
          <Button 
            variant="outline" 
            size="sm" 
            className="mt-4"
            onClick={() => setIsAddDialogOpen(true)}
          >
            <UserPlus className="w-4 h-4 mr-1" /> Add Member
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          {accessEntries.map((entry) => {
            const user = users.find(u => u.id === entry.user_id);
            const resource = resources.find(r => r.id === entry.resource_id);
            
            return (
              <div 
                key={entry.id} 
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                <div className="flex items-center">
                  {getAccessLevelIcon(entry.access_level)}
                  <div className="ml-2">
                    <p className="text-sm font-medium">{user?.username || "Unknown User"}</p>
                    <p className="text-xs text-gray-500">
                      {resource?.name || entry.resource_id} ({entry.resource_type.toLowerCase()})
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {getAccessLevelBadge(entry.access_level)}
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => handleRemoveAccess(entry.id)}
                    className="text-red-500 hover:text-red-700 p-1 h-auto"
                  >
                    Remove
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
