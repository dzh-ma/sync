import { NextRequest, NextResponse } from "next/server"

// Define energy rate in AED per kWh
const ENERGY_RATE = 0.45 // AED per kWh

// MongoDB URL
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function GET(request: NextRequest) {
  // Extract query parameters
  const searchParams = request.nextUrl.searchParams
  const timeRange = searchParams.get("timeRange") || "week"
  const userId = searchParams.get("userId")
  const householdId = searchParams.get("householdId")

  console.log(`Statistics API request: timeRange=${timeRange}, userId=${userId}, householdId=${householdId}`)

  if (!userId && !householdId) {
    console.warn("Statistics API: Missing userId or householdId parameter")
    return NextResponse.json(
      { error: "Missing userId or householdId parameter" },
      { status: 400 }
    )
  }

  try {
    // Fetch statistics from MongoDB via backend
    const timestamp = Date.now() // Cache busting
    let statsUrl = `${BACKEND_URL}/api/statistics?timeRange=${timeRange}&_t=${timestamp}`
    
    // Add parameters only if they are available
    if (userId) statsUrl += `&userId=${encodeURIComponent(userId)}`
    if (householdId) statsUrl += `&householdId=${encodeURIComponent(householdId)}`
    
    console.log(`Fetching statistics from backend: ${statsUrl}`)
    
    try {
      const statsResponse = await fetch(statsUrl, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        cache: "no-store", // Don't cache these requests
      })

      if (!statsResponse.ok) {
        const errorText = await statsResponse.text()
        console.error(`Failed to fetch statistics: ${statsResponse.status} ${statsResponse.statusText}`)
        console.error(`Error details: ${errorText}`)
        
        // Return empty stats instead of fake data
        return NextResponse.json(generateEmptyStatistics())
      }

      const statistics = await statsResponse.json()
      console.log(`Successfully fetched statistics from database. Energy consumed: ${statistics.totalEnergyConsumed}`)
      
      return NextResponse.json(statistics)
    } catch (fetchError: any) {
      console.error("Network error fetching statistics:", fetchError.message)
      return NextResponse.json(
        generateEmptyStatistics(),
        { status: 500 }
      )
    }
  } catch (error: any) {
    console.error("Error in statistics API:", error.message, error.stack)
    
    // Return empty data structure instead of fake data
    return NextResponse.json(
      generateEmptyStatistics(),
      { status: 500 }
    )
  }
}

// Function to generate empty statistics structure when no data is available
function generateEmptyStatistics() {
  return {
    energyData: [],
    deviceTypeData: [],
    roomData: [],
    totalEnergyConsumed: 0,
    totalCost: 0,
    mostActiveRoom: { name: "None", consumption: 0 },
    energySavings: 0
  };
}

// Calculate real statistics from MongoDB device data
function calculateRealStatistics(devices: any[], rooms: any[], timeRange: string) {
  console.log("Calculating REAL statistics from MongoDB data")
  
  // Calculate time window based on timeRange
  const now = new Date()
  let startDate = new Date()
  
  switch (timeRange) {
    case "day":
      startDate.setDate(now.getDate() - 1)
      break
    case "week":
      startDate.setDate(now.getDate() - 7)
      break
    case "month":
      startDate.setMonth(now.getMonth() - 1)
      break
    case "year":
      startDate.setFullYear(now.getFullYear() - 1)
      break
    default:
      startDate.setDate(now.getDate() - 7) // Default to week
  }

  console.log(`Time range: ${timeRange}, from ${startDate.toISOString()} to ${now.toISOString()}`)
  
  // Calculate total energy consumed for all devices
  let totalEnergyConsumed = 0
  
  // Track energy consumption by device type
  const deviceTypeMap = new Map<string, number>()
  
  // Track energy consumption by room
  const roomMap = new Map<string, number>()
  
  // Create energy usage data points over time
  const energyTimePoints: Map<string, number> = new Map()
  
  // Process each device
  devices.forEach((device: any) => {
    // Get device properties
    const deviceName = device.name || device.device_name || "Unknown Device"
    const deviceType = device.type || device.deviceType || "unknown"
    const deviceRoom = device.room || "unknown"
    const deviceStatus = device.status || "off"
    const energyUsagePerHour = device.energy_usage_per_hour || 0
    const lastStatusChange = device.last_status_change ? new Date(device.last_status_change) : null
    const totalEnergyForDevice = device.total_energy_consumed || 0
    
    console.log(`Processing device: ${deviceName} (${deviceType}) in ${deviceRoom}`)
    console.log(`Status: ${deviceStatus}, Energy per hour: ${energyUsagePerHour}, Last status change: ${lastStatusChange}`)
    
    // Calculate energy consumed by this device during the time period
    let deviceEnergyConsumed = 0
    
    if (deviceStatus === "on" && lastStatusChange && energyUsagePerHour > 0) {
      // Calculate how long the device has been on during our time range
      const deviceOnTime = lastStatusChange > startDate ? lastStatusChange : startDate
      const hoursSinceOn = (now.getTime() - deviceOnTime.getTime()) / (1000 * 60 * 60)
      
      // Calculate energy consumed (kWh)
      deviceEnergyConsumed = (energyUsagePerHour * hoursSinceOn) / 1000
      console.log(`Device has been on for ${hoursSinceOn.toFixed(2)} hours, consuming ${deviceEnergyConsumed.toFixed(2)} kWh`)
    } else {
      // Use the total energy consumed if recorded in the database
      deviceEnergyConsumed = totalEnergyForDevice || 0
      console.log(`Using recorded total energy: ${deviceEnergyConsumed.toFixed(2)} kWh`)
    }
    
    // Add to total energy consumed
    totalEnergyConsumed += deviceEnergyConsumed
    
    // Add to device type map
    const currentTypeConsumption = deviceTypeMap.get(deviceType) || 0
    deviceTypeMap.set(deviceType, currentTypeConsumption + deviceEnergyConsumed)
    
    // Add to room map
    const currentRoomConsumption = roomMap.get(deviceRoom) || 0
    roomMap.set(deviceRoom, currentRoomConsumption + deviceEnergyConsumed)
    
    // Add to energy time points data for charts
    if (deviceStatus === "on" && lastStatusChange && energyUsagePerHour > 0) {
      // Create energy data points based on the time range
      const interval = getIntervalForTimeRange(timeRange)
      
      // For each interval, add the device's energy consumption
      for (let timestamp = startDate.getTime(); timestamp <= now.getTime(); timestamp += interval) {
        const timeKey = new Date(timestamp).toISOString()
        
        // Only add energy for times after the device was turned on
        if (timestamp >= lastStatusChange.getTime()) {
          const hourlyConsumption = energyUsagePerHour / 1000 // Convert to kWh
          const existingValue = energyTimePoints.get(timeKey) || 0
          energyTimePoints.set(timeKey, existingValue + hourlyConsumption)
        }
      }
    }
  })
  
  // Calculate total cost
  const totalCost = totalEnergyConsumed * ENERGY_RATE
  
  // Format energy data for chart display
  const energyData = Array.from(energyTimePoints.entries())
    .map(([timestamp, value]) => ({
      timestamp,
      value
    }))
    .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
  
  // If there are no energy data points from devices being on, create some empty data points for the chart
  if (energyData.length === 0) {
    const interval = getIntervalForTimeRange(timeRange)
    for (let timestamp = startDate.getTime(); timestamp <= now.getTime(); timestamp += interval) {
      energyData.push({
        timestamp: new Date(timestamp).toISOString(),
        value: 0
      })
    }
  }
  
  // Format device type data
  const deviceTypeData = Array.from(deviceTypeMap.entries())
    .filter(([_, consumption]) => consumption > 0) // Only include types with consumption
    .map(([type, consumption]) => ({
    type,
    consumption,
    percentage: totalEnergyConsumed > 0 ? (consumption / totalEnergyConsumed) * 100 : 0
  }))
  
  // Format room data
  const roomData = Array.from(roomMap.entries())
    .filter(([_, consumption]) => consumption > 0) // Only include rooms with consumption
    .map(([name, consumption]) => ({
    name,
    consumption,
    percentage: totalEnergyConsumed > 0 ? (consumption / totalEnergyConsumed) * 100 : 0
  }))
  
  // Determine most active room
  let mostActiveRoom = { name: "None", consumption: 0 }
  if (roomData.length > 0) {
    const sortedRooms = [...roomData].sort((a, b) => b.consumption - a.consumption)
    mostActiveRoom = { name: sortedRooms[0].name, consumption: sortedRooms[0].consumption }
  }
  
  // Calculate a realistic energy savings value based on average consumption
  // For the real app this would compare to historical data, but we'll use a fixed value for now
  const energySavings = totalEnergyConsumed > 0 ? 10 : 0 // 10% savings when devices are active
  
  return {
    energyData,
    deviceTypeData,
    roomData,
    totalEnergyConsumed,
    totalCost,
    mostActiveRoom,
    energySavings
  }
}

// Helper function to get time interval based on time range
function getIntervalForTimeRange(timeRange: string): number {
  switch (timeRange) {
    case "day":
      return 60 * 60 * 1000 // 1 hour in milliseconds
    case "week":
      return 24 * 60 * 60 * 1000 // 1 day in milliseconds
    case "month":
      return 24 * 60 * 60 * 1000 // 1 day in milliseconds
    case "year":
      return 30 * 24 * 60 * 60 * 1000 // approx. 1 month in milliseconds
    default:
      return 24 * 60 * 60 * 1000 // Default to 1 day
  }
}

