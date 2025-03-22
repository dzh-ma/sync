"use client";

import { useState, useEffect } from "react";
import { Loader2, Zap, ZapOff, Lightbulb, Clock, ThermometerSun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { toast } from "@/components/ui/use-toast";
import { useRouter } from "next/navigation";

interface Automation {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  trigger_type: string;
  action_type: string;
  execution_count: number;
}

interface AutomationWidgetProps {
  userId?: string;
  token?: string;
  apiUrl?: string;
}

export function AutomationWidget({ userId, token, apiUrl = 'http://localhost:8000/api/v1' }: AutomationWidgetProps) {
  const router = useRouter();
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAutomations = async () => {
      if (!userId || !token) {
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        
        const response = await fetch(`${apiUrl}/automations?user_id=${userId}&limit=5`, {
          headers: {
            'Authorization': `Basic ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!response.ok) {
          throw new Error(`Error fetching automations: ${response.status}`);
        }

        const data = await response.json();
        setAutomations(data);
      } catch (err) {
        console.error("Failed to fetch automations:", err);
        setError("Failed to load automations. Please try again.");
        
        // Set fallback data for development
        setAutomations([
          { 
            id: "1", 
            name: "Night Mode", 
            description: "Turn off lights at 11pm", 
            enabled: true,
            trigger_type: "TIME",
            action_type: "DEVICE_CONTROL",
            execution_count: 42
          },
          { 
            id: "2", 
            name: "Morning Warmup", 
            description: "Turn on heating at 7am", 
            enabled: true,
            trigger_type: "TIME",
            action_type: "DEVICE_CONTROL",
            execution_count: 23
          },
          { 
            id: "3", 
            name: "Away Mode", 
            description: "Secure home when no one is present", 
            enabled: false,
            trigger_type: "LOCATION",
            action_type: "SCENE_ACTIVATION",
            execution_count: 15
          }
        ]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAutomations();
  }, [userId, token, apiUrl]);

  const toggleAutomation = async (automation: Automation) => {
    if (!userId || !token) return;
    
    try {
      // Update optimistically in UI
      const newEnabled = !automation.enabled;
      setAutomations(prev => 
        prev.map(a => a.id === automation.id ? { ...a, enabled: newEnabled } : a)
      );
      
      // Send update to API
      const response = await fetch(`${apiUrl}/automations/${automation.id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Basic ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          enabled: newEnabled
        })
      });

      if (!response.ok) {
        throw new Error(`Error updating automation: ${response.status}`);
      }
      
      // Get the updated automation
      const updatedAutomation = await response.json();
      
      // Update state with server response
      setAutomations(prev => 
        prev.map(a => a.id === automation.id ? updatedAutomation : a)
      );
      
      toast({
        title: "Automation Updated",
        description: `${automation.name} is now ${newEnabled ? 'enabled' : 'disabled'}.`,
      });
    } catch (err) {
      console.error("Failed to toggle automation:", err);
      
      // Revert the optimistic update
      setAutomations(prev => 
        prev.map(a => a.id === automation.id ? automation : a)
      );
      
      toast({
        title: "Error",
        description: "Failed to update automation. Please try again.",
        variant: "destructive"
      });
    }
  };

  const getAutomationIcon = (automation: Automation) => {
    if (automation.trigger_type === "TIME") {
      return <Clock className="w-4 h-4 text-gray-500 mr-2" />;
    } else if (automation.action_type === "DEVICE_CONTROL" && automation.name.toLowerCase().includes("light")) {
      return <Lightbulb className="w-4 h-4 text-yellow-500 mr-2" />;
    } else if (automation.action_type === "DEVICE_CONTROL" && 
              (automation.name.toLowerCase().includes("heat") || 
               automation.name.toLowerCase().includes("temp"))) {
      return <ThermometerSun className="w-4 h-4 text-orange-500 mr-2" />;
    }
    return <Zap className="w-4 h-4 text-blue-500 mr-2" />;
  };

  const navigateToAutomations = () => {
    router.push('/automations');
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-4 h-full">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500 mb-2" />
        <p className="text-sm text-gray-500">Loading automations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-4 h-full">
        <ZapOff className="w-8 h-8 text-red-500 mb-2" />
        <p className="text-sm text-gray-500">{error}</p>
        <Button 
          variant="outline" 
          size="sm" 
          className="mt-2"
          onClick={() => setIsLoading(true)}
        >
          Retry
        </Button>
      </div>
    );
  }

  if (automations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-4 h-full">
        <ZapOff className="w-8 h-8 text-gray-400 mb-2" />
        <p className="text-sm text-gray-500">No automations found</p>
        <Button 
          variant="outline" 
          size="sm" 
          className="mt-2"
          onClick={navigateToAutomations}
        >
          Create New
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Automations</h3>
        <span className="text-xs text-gray-500">
          {automations.filter(a => a.enabled).length} active
        </span>
      </div>
      <div className="space-y-3">
        {automations.map((automation) => (
          <div key={automation.id} className="flex items-center justify-between">
            <div className="flex items-center overflow-hidden">
              {getAutomationIcon(automation)}
              <div className="truncate">
                <p className="text-sm font-medium">{automation.name}</p>
                <p className="text-xs text-gray-500 truncate">{automation.description}</p>
              </div>
            </div>
            <div>
              <Switch 
                checked={automation.enabled} 
                onCheckedChange={() => toggleAutomation(automation)}
                aria-label={`Toggle ${automation.name}`}
              />
            </div>
          </div>
        ))}
      </div>
      <Button 
        variant="outline" 
        size="sm" 
        className="w-full mt-2"
        onClick={navigateToAutomations}
      >
        View All Automations
      </Button>
    </div>
  );
}
