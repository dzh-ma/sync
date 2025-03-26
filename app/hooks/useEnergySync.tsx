import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Custom hook to synchronize energy consumption data with the backend
 * @returns Functions to trigger synchronization manually
 */
export function useEnergySync() {
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);

  // Function to get user info from localStorage
  const getUserInfo = useCallback(() => {
    const storedUser = localStorage.getItem("currentUser");
    const storedMember = localStorage.getItem("currentMember");
    
    let userId: string | undefined = undefined;
    let householdId: string | undefined = undefined;
    
    if (storedUser) {
      const currentUser = JSON.parse(storedUser);
      userId = currentUser.id;
      householdId = currentUser.householdId;
    } else if (storedMember) {
      const currentMember = JSON.parse(storedMember);
      userId = currentMember.id;
      householdId = currentMember.householdId;
    }
    
    return { userId, householdId };
  }, []);

  // Function to trigger statistics collection
  const collectStatistics = useCallback(async () => {
    const { userId, householdId } = getUserInfo();
    
    if (!userId) {
      console.warn("No user ID found for statistics collection");
      return false;
    }
    
    try {
      const statsResponse = await fetch(`/api/statistics/collect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId,
          householdId: householdId || ''
        }),
      });
      
      return statsResponse.ok;
    } catch (error) {
      console.error("Error collecting statistics:", error);
      return false;
    }
  }, [getUserInfo]);

  // Function to sync device energy consumption from backend to localStorage
  const syncEnergyConsumption = useCallback(async () => {
    try {
      setIsSyncing(true);
      const { userId, householdId } = getUserInfo();
      
      if (!userId) {
        console.warn("No user ID found for energy sync");
        setIsSyncing(false);
        return false;
      }
      
      // First collect statistics to ensure latest data
      const statsSuccess = await collectStatistics();
      if (!statsSuccess) {
        console.warn("Failed to collect statistics during energy sync");
      }
      
      // Then fetch updated device data
      const response = await axios.get(`${API_URL}/api/user/devices`, {
        params: {
          user_id: userId,
          household_id: householdId || ''
        }
      });
      
      const backendDevices = response.data || [];
      
      // Get current devices from localStorage
      const storedDevices = JSON.parse(localStorage.getItem("devices") || "[]");
      
      // Update energy consumption values from backend
      const updatedDevices = storedDevices.map((device: any) => {
        const backendDevice = backendDevices.find((bd: any) => bd.name === device.name);
        if (backendDevice && typeof backendDevice.total_energy_consumed === 'number') {
          return {
            ...device,
            totalEnergyConsumed: backendDevice.total_energy_consumed
          };
        }
        return device;
      });
      
      // Save updated devices back to localStorage
      localStorage.setItem("devices", JSON.stringify(updatedDevices));
      
      setLastSyncTime(new Date());
      console.log("Energy consumption synchronization complete");
      
      setIsSyncing(false);
      return true;
    } catch (error) {
      console.error("Error syncing energy consumption:", error);
      setIsSyncing(false);
      return false;
    }
  }, [getUserInfo, collectStatistics]);

  // Set up automatic synchronization on an interval
  useEffect(() => {
    // Sync energy consumption on component mount
    syncEnergyConsumption();
    
    // Set up interval for periodic sync
    const syncInterval = setInterval(() => {
      syncEnergyConsumption();
    }, 5 * 60 * 1000); // Sync every 5 minutes
    
    // Clean up interval on unmount
    return () => clearInterval(syncInterval);
  }, [syncEnergyConsumption]);

  return {
    syncEnergyConsumption,
    collectStatistics,
    isSyncing,
    lastSyncTime
  };
}

export default useEnergySync; 