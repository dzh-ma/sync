// components/automation-widget.tsx
import { useState, useEffect } from "react";
import { Plus, AlertCircle, Clock, Calendar, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "@/components/ui/use-toast";

interface Automation {
  id: string;
  name: string;
  description: string;
  trigger_type: string;
  action_type: string;
  enabled: boolean;
  last_triggered: string | null;
  execution_count: number;
}

interface Device {
  id: string;
  name: string;
  type: string;
}

interface AutomationWidgetProps {
  userId: string;
  createAuthHeaders: () => Record<string, string>;
  apiUrl: string;
  isDarkMode?: boolean;
}

export function AutomationWidget({ userId, createAuthHeaders, apiUrl, isDarkMode = false }: AutomationWidgetProps) {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newAutomation, setNewAutomation] = useState({
    name: '',
    description: '',
    device_id: '',
    trigger_type: 'time',
    action_type: 'device_control',
    trigger_data: {},
    action_data: {}
  });
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  // Fetch automations and devices
  useEffect(() => {
    const fetchData = async () => {
      if (!userId) return;

      try {
        setLoading(true);
        
        // Fetch automations
        const automationResponse = await fetch(`${apiUrl}/automations?user_id=${userId}`, {
          headers: createAuthHeaders()
        });
        
        if (!automationResponse.ok) {
          throw new Error(`Error fetching automations: ${automationResponse.statusText}`);
        }
        
        const automationsData = await automationResponse.json();
        setAutomations(automationsData.slice(0, 4)); // Show only first 4 automations
        
        // Fetch devices
        const devicesResponse = await fetch(`${apiUrl}/devices?user_id=${userId}`, {
          headers: createAuthHeaders()
        });
        
        if (!devicesResponse.ok) {
          throw new Error(`Error fetching devices: ${devicesResponse.statusText}`);
        }
        
        const devicesData = await devicesResponse.json();
        setDevices(devicesData);
        
        // Pre-select first device if available
        if (devicesData.length > 0) {
          setNewAutomation(prev => ({
            ...prev,
            device_id: devicesData[0].id
          }));
        }
        
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to load automations");
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [userId, apiUrl, createAuthHeaders]);

  // Toggle automation enabled/disabled
  const toggleAutomation = async (id: string, currentStatus: boolean) => {
    try {
      const response = await fetch(`${apiUrl}/automations/${id}`, {
        method: 'PATCH',
        headers: createAuthHeaders(),
        body: JSON.stringify({
          enabled: !currentStatus
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to update automation: ${response.statusText}`);
      }
      
      // Update local state
      setAutomations(automations.map(automation => 
        automation.id === id 
          ? {...automation, enabled: !currentStatus} 
          : automation
      ));
      
      toast({
        title: "Automation updated",
        description: `Automation ${!currentStatus ? 'enabled' : 'disabled'} successfully.`
      });
    } catch (error) {
      console.error("Error toggling automation:", error);
      toast({
        title: "Error",
        description: "Failed to update automation.",
        variant: "destructive"
      });
    }
  };

  // Create new automation
  const createAutomation = async () => {
    try {
      // Set trigger data
      let trigger_data = {};
      if (newAutomation.trigger_type === 'time') {
        trigger_data = {
          time: "08:00",
          days: ["mon", "tue", "wed", "thu", "fri"]
        };
      }
      
      // Set action data
      let action_data = {};
      if (newAutomation.action_type === 'device_control') {
        action_data = {
          device_id: newAutomation.device_id,
          action: "toggle"
        };
      }
      
      const response = await fetch(`${apiUrl}/automations`, {
        method: 'POST',
        headers: createAuthHeaders(),
        body: JSON.stringify({
          user_id: userId,
          device_id: newAutomation.device_id,
          name: newAutomation.name,
          description: newAutomation.description,
          trigger_type: newAutomation.trigger_type,
          trigger_data: trigger_data,
          action_type: newAutomation.action_type,
          action_data: action_data,
          enabled: true
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create automation: ${response.statusText}`);
      }
      
      const newAutomationData = await response.json();
      
      // Update local state
      setAutomations([newAutomationData, ...automations.slice(0, 3)]);
      
      // Reset form and close dialog
      setNewAutomation({
        name: '',
        description: '',
        device_id: devices.length > 0 ? devices[0].id : '',
        trigger_type: 'time',
        action_type: 'device_control',
        trigger_data: {},
        action_data: {}
      });
      setIsDialogOpen(false);
      
      toast({
        title: "Automation created",
        description: "Your new automation has been created successfully."
      });
    } catch (error) {
      console.error("Error creating automation:", error);
      toast({
        title: "Error",
        description: "Failed to create automation.",
        variant: "destructive"
      });
    }
  };

  if (loading) {
    return (
      <div className="space-y-2">
        <h3 className="text-sm font-medium">Automations</h3>
        <div className="animate-pulse space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-10 bg-gray-200 rounded-md"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-2">
        <h3 className="text-sm font-medium">Automations</h3>
        <div className={`p-4 rounded-md ${isDarkMode ? 'bg-red-900/20' : 'bg-red-50'} text-red-500`}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <h3 className="text-sm font-medium">Automations</h3>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <Plus className="h-4 w-4" />
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Automation</DialogTitle>
              <DialogDescription>
                Set up a new automation for your smart home devices.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  value={newAutomation.name}
                  onChange={(e) =>
                    setNewAutomation({ ...newAutomation, name: e.target.value })
                  }
                  placeholder="Morning Routine"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={newAutomation.description}
                  onChange={(e) =>
                    setNewAutomation({
                      ...newAutomation,
                      description: e.target.value,
                    })
                  }
                  placeholder="Turn on lights at 7:00 AM"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="device">Device</Label>
                <Select
                  value={newAutomation.device_id}
                  onValueChange={(value) =>
                    setNewAutomation({ ...newAutomation, device_id: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a device" />
                  </SelectTrigger>
                  <SelectContent>
                    {devices.map((device) => (
                      <SelectItem key={device.id} value={device.id}>
                        {device.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="trigger">Trigger Type</Label>
                <Select
                  value={newAutomation.trigger_type}
                  onValueChange={(value) =>
                    setNewAutomation({
                      ...newAutomation,
                      trigger_type: value,
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a trigger" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="time">Time</SelectItem>
                    <SelectItem value="sensor">Sensor</SelectItem>
                    <SelectItem value="device_state">Device State</SelectItem>
                    <SelectItem value="location">Location</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="action">Action Type</Label>
                <Select
                  value={newAutomation.action_type}
                  onValueChange={(value) =>
                    setNewAutomation({
                      ...newAutomation,
                      action_type: value,
                    })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select an action" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="device_control">Device Control</SelectItem>
                    <SelectItem value="notification">Notification</SelectItem>
                    <SelectItem value="scene_activation">Scene Activation</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={createAutomation}>Create</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
      <div className="space-y-2">
        {automations.length === 0 ? (
          <div className={`p-4 rounded-md ${isDarkMode ? 'bg-gray-800' : 'bg-gray-100'} text-center`}>
            <p className="text-sm text-gray-500">No automations set up yet</p>
            <Button
              variant="link"
              size="sm"
              className="mt-1"
              onClick={() => setIsDialogOpen(true)}
            >
              Create your first automation
            </Button>
          </div>
        ) : (
          automations.map((automation) => (
            <div
              key={automation.id}
              className={`p-2 rounded-lg flex items-center justify-between ${
                isDarkMode ? 'bg-gray-800' : 'bg-gray-100'
              }`}
            >
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-full ${automation.enabled ? 'bg-green-100 text-green-600' : 'bg-gray-200 text-gray-500'}`}>
                  {automation.trigger_type === 'time' ? (
                    <Clock className="h-4 w-4" />
                  ) : automation.trigger_type === 'location' ? (
                    <Calendar className="h-4 w-4" />
                  ) : (
                    <AlertCircle className="h-4 w-4" />
                  )}
                </div>
                <div>
                  <h4 className="text-sm font-medium">{automation.name}</h4>
                  <p className="text-xs text-gray-500 truncate max-w-[150px]">
                    {automation.description}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-1">
                <div className="text-xs text-right mr-2">
                  <p className="text-gray-500">
                    {automation.last_triggered 
                      ? new Date(automation.last_triggered).toLocaleDateString() 
                      : 'Never run'}
                  </p>
                  <p className="text-gray-500">Runs: {automation.execution_count}</p>
                </div>
                <Switch
                  checked={automation.enabled}
                  onCheckedChange={() => toggleAutomation(automation.id, automation.enabled)}
                  size="sm"
                />
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
