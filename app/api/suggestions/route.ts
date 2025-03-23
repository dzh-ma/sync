import { type NextRequest, NextResponse } from "next/server"

// Device type definitions
interface Device {
  id: string
  name: string
  type: string
  room: string
  status: "on" | "off"
  lastStatusChange?: number
  temperature?: number
  brightness?: number
  speed?: number
  powerConsumption?: number
  totalEnergyConsumed?: number
  usageHistory?: Array<{
    timestamp: number
    duration: number
    powerConsumption: number
    energyConsumed: number
  }>
}

interface Suggestion {
  title: string
  description: string
  icon: string
  iconColor: string
  saving: string
  impact?: string
  action?: string
  category?: string
  details?: string[]
  deviceId?: string
}

// Device thresholds and power consumption data
const deviceThresholds = {
  light: {
    dailyUsageHours: 5, // hours per day
    standbyPower: 0.5, // watts
    activePower: 8.5, // watts
    usageThreshold: 2, // hours - only suggest if usage exceeds this
    energyThreshold: 1, // kWh per month - only suggest if energy exceeds this
    brightnessThreshold: 80, // percentage - suggest if brightness exceeds this
  },
  thermostat: {
    optimalTempRange: [21, 24], // Celsius
    dailyUsageHours: 8,
    standbyPower: 1.5,
    activePower: 1500,
    usageThreshold: 4, // hours
    energyThreshold: 20, // kWh per month
  },
  tv: {
    dailyUsageHours: 4,
    standbyPower: 1.5,
    activePower: 100,
    usageThreshold: 3, // hours
    energyThreshold: 10, // kWh per month
  },
  fan: {
    dailyUsageHours: 6,
    standbyPower: 1.0,
    activePower: 60,
    usageThreshold: 4, // hours
    energyThreshold: 8, // kWh per month
    speedThreshold: 3, // Changed from 80 to 3 (for speed range 1-5)
  },
  speaker: {
    dailyUsageHours: 3,
    standbyPower: 1.0,
    activePower: 20,
    usageThreshold: 2, // hours
    energyThreshold: 3, // kWh per month
  },
  refrigerator: {
    dailyUsageHours: 24, // always on
    standbyPower: 0,
    activePower: 150,
    usageThreshold: 24, // hours (always on)
    energyThreshold: 50, // kWh per month
  },
  washer: {
    dailyUsageHours: 1,
    standbyPower: 2.0,
    activePower: 500,
    usageThreshold: 1, // hours
    energyThreshold: 15, // kWh per month
  },
  dryer: {
    dailyUsageHours: 1,
    standbyPower: 2.0,
    activePower: 3000,
    usageThreshold: 1, // hours
    energyThreshold: 30, // kWh per month
  },
  dishwasher: {
    dailyUsageHours: 1,
    standbyPower: 2.0,
    activePower: 1200,
    usageThreshold: 1, // hours
    energyThreshold: 15, // kWh per month
  },
  oven: {
    dailyUsageHours: 1,
    standbyPower: 2.0,
    activePower: 2000,
    usageThreshold: 1, // hours
    energyThreshold: 20, // kWh per month
  },
  microwave: {
    dailyUsageHours: 0.5,
    standbyPower: 3.0,
    activePower: 1000,
    usageThreshold: 0.5, // hours
    energyThreshold: 8, // kWh per month
  },
  computer: {
    dailyUsageHours: 4,
    standbyPower: 2.0,
    activePower: 200,
    usageThreshold: 3, // hours
    energyThreshold: 15, // kWh per month
  },
  printer: {
    dailyUsageHours: 0.5,
    standbyPower: 2.0,
    activePower: 50,
    usageThreshold: 0.5, // hours
    energyThreshold: 3, // kWh per month
  },
  router: {
    dailyUsageHours: 24, // always on
    standbyPower: 0,
    activePower: 7,
    usageThreshold: 24, // hours (always on)
    energyThreshold: 5, // kWh per month
  },
}

// Suggestion templates
const suggestionTemplates = {
  excessiveUsage: {
    light: {
      title: "Optimize Lighting Usage",
      description: (room: string, hoursOn: number, percentOver: number) =>
        `Your ${room} lights are on for ${hoursOn}h daily, which is ${percentOver}% above average.`,
      icon: "Lightbulb",
      iconColor: "text-yellow-500",
      saving: (potentialSaving: number) => `Potential saving: ${potentialSaving} kWh/month`,
      impact: (costSaving: string) => `Reduce your lighting bill by up to ${costSaving}`,
      action: "Adjust Settings",
      category: "Energy Efficiency",
    },
    thermostat: {
      title: "Optimize Temperature Settings",
      description: (room: string, currentTemp: number, optimalTemp: number) =>
        `Your ${room} temperature is set to ${currentTemp}°C. Consider adjusting to ${optimalTemp}°C.`,
      icon: "Thermometer",
      iconColor: "text-red-500",
      saving: (potentialSaving: number) => `Potential saving: ${potentialSaving} kWh/month`,
      impact: (co2Reduction: number) => `Environmental Impact: Reduce CO2 emissions by ${co2Reduction}kg`,
      action: "Adjust Settings",
      category: "Energy Efficiency",
    },
    tv: {
      title: "Standby Power Detection",
      description: (room: string) => `Your ${room} TV is often left in standby mode, consuming unnecessary power.`,
      icon: "Tv",
      iconColor: "text-purple-500",
      saving: (potentialSaving: number) => `Potential saving: ${potentialSaving} kWh/month`,
      impact: () => "Reduce phantom power consumption",
      action: "Adjust Settings",
      category: "Energy Efficiency",
    },
    fan: {
      title: "Fan Usage Optimization",
      description: (room: string) => `Your ${room} fan runs for extended periods. Consider using a timer.`,
      icon: "Fan",
      iconColor: "text-blue-500",
      saving: (potentialSaving: number) => `Potential saving: ${potentialSaving} kWh/month`,
      impact: () => "Extend device lifespan and reduce energy waste",
      action: "Adjust Settings",
      category: "Energy Efficiency",
    },
    default: {
      title: "Extended Device Usage",
      description: (deviceName: string, room: string, hoursOn: number) =>
        `Your ${deviceName} in ${room} has been on for ${hoursOn.toFixed(1)} hours, which is above average.`,
      icon: "Zap",
      iconColor: "text-orange-500",
      saving: (potentialSaving: number) => `Potential saving: ${potentialSaving} kWh/month`,
      impact: (costSaving: string) => `Reduce your energy bill by up to ${costSaving}`,
      action: "Adjust Settings",
      category: "Energy Efficiency",
    },
  },
  highSettings: {
    light: {
      title: "High Brightness Detected",
      description: (room: string, brightness: number) =>
        `Your ${room} light is set to ${brightness}% brightness. Reducing it could save energy.`,
      icon: "Lightbulb",
      iconColor: "text-yellow-500",
      saving: (potentialSaving: number) => `Potential saving: ${potentialSaving} kWh/month`,
      impact: (costSaving: string) => `Reduce your lighting bill by up to ${costSaving}`,
      action: "Adjust Settings",
      category: "Energy Efficiency",
    },
    fan: {
      title: "High Fan Speed Detected",
      description: (room: string, speed: number) =>
        `Your ${room} fan is set to speed ${speed}. Reducing it could save energy.`,
      icon: "Fan",
      iconColor: "text-blue-500",
      saving: (potentialSaving: number) => `Potential saving: ${potentialSaving} kWh/month`,
      impact: (costSaving: string) => `Reduce your energy bill by up to ${costSaving}`,
      action: "Adjust Settings",
      category: "Energy Efficiency",
    },
    thermostat: {
      title: "High Temperature Detected",
      description: (room: string, temperature: number, optimalTemp: number) =>
        `Your ${room} thermostat is set to ${temperature}°C. Reducing to ${optimalTemp}°C could save energy.`,
      icon: "Thermometer",
      iconColor: "text-red-500",
      saving: (potentialSaving: number) => `Potential saving: ${potentialSaving} kWh/month`,
      impact: (costSaving: string) => `Reduce your heating bill by up to ${costSaving}`,
      action: "Adjust Settings",
      category: "Energy Efficiency",
    },
  },
  patternDetected: {
    title: "Usage Pattern Detected",
    description: (deviceName: string, room: string) =>
      `We've detected a regular pattern for your ${deviceName} in ${room}. Would you like to automate this?`,
    icon: "Clock",
    iconColor: "text-green-500",
    saving: (potentialSaving: number) => `Potential saving: ${potentialSaving} kWh/month`,
    impact: () => "Convenience: Automate daily routines",
    action: "Create Automation",
    category: "Automation",
  },
  highUsage: {
    title: "High Usage Detected",
    description: (deviceName: string, room: string, usageHours: number) =>
      `Your ${deviceName} in ${room} has been running for ${usageHours.toFixed(1)} hours today, which is above average.`,
    icon: "Zap",
    iconColor: "text-orange-500",
    saving: (potentialSaving: number) => `Potential saving: ${potentialSaving} kWh/month`,
    impact: (costSaving: string) => `Reduce your energy bill by up to ${costSaving}`,
    action: "Adjust Settings",
    category: "Energy Efficiency",
  },
  highConsumption: {
    title: "High Energy Consumption",
    description: (deviceName: string, room: string, consumption: number) =>
      `Your ${deviceName} in ${room} has consumed ${consumption.toFixed(1)} kWh this month, which is above average.`,
    icon: "Zap",
    iconColor: "text-orange-500",
    saving: (potentialSaving: number) => `Potential saving: ${potentialSaving} kWh/month`,
    impact: (costSaving: string) => `Reduce your energy bill by up to ${costSaving}`,
    action: "Adjust Settings",
    category: "Energy Efficiency",
  },
}

// Helper functions
function getDevicePower(device: Device): number {
  if (device.powerConsumption) {
    return device.powerConsumption
  } else if (deviceThresholds[device.type]) {
    return deviceThresholds[device.type].activePower
  } else {
    return 10 // Default value
  }
}

function calculateTotalEnergyConsumed(device: Device): number {
  // If the device has usage history, calculate from that
  if (device.usageHistory && device.usageHistory.length > 0) {
    return device.usageHistory.reduce((total, record) => total + record.energyConsumed, 0)
  }

  // Otherwise estimate based on last status change
  const lastStatusChange = device.lastStatusChange || Date.now() - 3600000 * 24 // Default to 24 hours ago
  const now = Date.now()
  const hoursOn = (now - lastStatusChange) / (1000 * 60 * 60)

  if (device.status === "on") {
    const power = getDevicePower(device)
    return (power * hoursOn) / 1000 // kWh
  }

  return device.totalEnergyConsumed || 0
}

function checkExcessiveUsage(device: Device, room: string): Suggestion | null {
  const deviceType = device.type
  if (!deviceThresholds[deviceType]) {
    return null
  }

  const thresholds = deviceThresholds[deviceType]

  // Calculate how long the device has been on
  const lastStatusChange = device.lastStatusChange || Date.now() - 3600000 * 6 // Default to 6 hours ago
  const now = Date.now()
  const hoursOn = (now - lastStatusChange) / (1000 * 60 * 60)

  // Only suggest if the device has been on for longer than the threshold
  if (hoursOn < thresholds.usageThreshold) {
    return null
  }

  // Calculate potential savings
  const percentOver = Math.round((hoursOn / thresholds.dailyUsageHours - 1) * 100)
  if (percentOver < 10) {
    // Only suggest if usage is at least 10% over threshold (lowered from 20%)
    return null
  }

  const activePower = device.powerConsumption || thresholds.activePower
  const potentialSaving = (((hoursOn - thresholds.dailyUsageHours) * activePower * 30) / 1000).toFixed(1) // kWh per month
  const costSaving = `${(Number.parseFloat(potentialSaving) * 0.45).toFixed(2)} AED` // Assuming 0.45 AED per kWh
  const co2Reduction = (Number.parseFloat(potentialSaving) * 0.5).toFixed(1) // kg CO2 per kWh

  // Get the appropriate template
  const template = suggestionTemplates.excessiveUsage[deviceType] || suggestionTemplates.excessiveUsage.default

  // For thermostats, check temperature settings
  let currentTemp = null
  let optimalTemp = null
  if (deviceType === "thermostat") {
    currentTemp = device.temperature || 22
    const optimalRange = thresholds.optimalTempRange
    if (currentTemp < optimalRange[0]) {
      optimalTemp = optimalRange[0]
    } else if (currentTemp > optimalRange[1]) {
      optimalTemp = optimalRange[1]
    } else {
      // Even if temperature is in optimal range, we still want to suggest if usage is excessive
      optimalTemp = currentTemp
    }
  }

  // Format the suggestion
  const suggestion: Suggestion = {
    title: template.title,
    description:
      deviceType === "thermostat"
        ? template.description(room, currentTemp, optimalTemp)
        : template.description(room, Number.parseFloat(hoursOn.toFixed(1)), percentOver),
    icon: template.icon,
    iconColor: template.iconColor,
    saving: template.saving(Number.parseFloat(potentialSaving)),
    impact: deviceType === "thermostat" ? template.impact(co2Reduction) : template.impact(costSaving),
    action: template.action,
    category: template.category,
    details: [
      `Current usage: ${hoursOn.toFixed(1)} hours per day`,
      `Recommended: ${thresholds.dailyUsageHours} hours per day`,
      `Device: ${device.name || deviceType.charAt(0).toUpperCase() + deviceType.slice(1)}`,
    ],
    deviceId: device.id,
  }

  return suggestion
}

function checkHighSettings(device: Device, room: string): Suggestion | null {
  const deviceType = device.type
  if (!deviceThresholds[deviceType]) {
    return null
  }

  const thresholds = deviceThresholds[deviceType]

  // Check for high brightness on lights
  if (deviceType === "light" && device.brightness && device.brightness > thresholds.brightnessThreshold) {
    const template = suggestionTemplates.highSettings.light
    const brightness = device.brightness

    // Calculate potential savings (assume 30% reduction in brightness = 20% energy saving)
    const activePower = device.powerConsumption || thresholds.activePower
    const potentialSaving = ((activePower * 0.2 * thresholds.dailyUsageHours * 30) / 1000).toFixed(1) // kWh per month
    const costSaving = `${(Number.parseFloat(potentialSaving) * 0.45).toFixed(2)} AED` // Assuming 0.45 AED per kWh

    const suggestion: Suggestion = {
      title: template.title,
      description: template.description(room, brightness),
      icon: template.icon,
      iconColor: template.iconColor,
      saving: template.saving(Number.parseFloat(potentialSaving)),
      impact: template.impact(costSaving),
      action: template.action,
      category: template.category,
      details: [
        `Current brightness: ${brightness}%`,
        `Recommended: 70-80% for most activities`,
        `Potential monthly savings: ${costSaving}`,
      ],
      deviceId: device.id,
    }

    return suggestion
  }

  // Check for high speed on fans
  if (deviceType === "fan" && device.speed) {
    // Convert speed if needed (our devices use 1-5 scale)
    const speed = device.speed
    const speedThreshold = thresholds.speedThreshold || 3

    // Only suggest if speed exceeds threshold
    if (speed > speedThreshold) {
      const template = suggestionTemplates.highSettings.fan

      // Calculate potential savings (assume 20% reduction in speed = 15% energy saving)
      const activePower = device.powerConsumption || thresholds.activePower
      const potentialSaving = ((activePower * 0.15 * thresholds.dailyUsageHours * 30) / 1000).toFixed(1) // kWh per month
      const costSaving = `${(Number.parseFloat(potentialSaving) * 0.45).toFixed(2)} AED` // Assuming 0.45 AED per kWh

      const suggestion: Suggestion = {
        title: template.title,
        description: template.description(room, speed),
        icon: template.icon,
        iconColor: template.iconColor,
        saving: template.saving(Number.parseFloat(potentialSaving)),
        impact: template.impact(costSaving),
        action: template.action,
        category: template.category,
        details: [
          `Current speed: ${speed}`,
          `Recommended: 2-3 for optimal comfort`,
          `Potential monthly savings: ${costSaving}`,
        ],
        deviceId: device.id,
      }

      return suggestion
    }
  }

  // Check for high temperature on thermostats
  if (deviceType === "thermostat" && device.temperature) {
    const temperature = device.temperature
    const optimalRange = thresholds.optimalTempRange

    // Only suggest if temperature is above the optimal range
    if (temperature > optimalRange[1]) {
      const template = suggestionTemplates.highSettings.thermostat
      const optimalTemp = optimalRange[1]

      // Calculate potential savings (assume 1°C reduction = 10% energy saving)
      const tempDifference = temperature - optimalTemp
      const activePower = device.powerConsumption || thresholds.activePower
      const potentialSaving = ((activePower * 0.1 * tempDifference * thresholds.dailyUsageHours * 30) / 1000).toFixed(1) // kWh per month
      const costSaving = `${(Number.parseFloat(potentialSaving) * 0.45).toFixed(2)} AED` // Assuming 0.45 AED per kWh

      const suggestion: Suggestion = {
        title: template.title,
        description: template.description(room, temperature, optimalTemp),
        icon: template.icon,
        iconColor: template.iconColor,
        saving: template.saving(Number.parseFloat(potentialSaving)),
        impact: template.impact(costSaving),
        action: template.action,
        category: template.category,
        details: [
          `Current temperature: ${temperature}°C`,
          `Recommended: ${optimalTemp}°C for optimal comfort and efficiency`,
          `Potential monthly savings: ${costSaving}`,
        ],
        deviceId: device.id,
      }

      return suggestion
    }
  }

  return null
}

function checkHighConsumption(device: Device, room: string): Suggestion | null {
  const deviceType = device.type
  if (!deviceThresholds[deviceType]) {
    return null
  }

  const thresholds = deviceThresholds[deviceType]

  // Calculate total energy consumed
  const totalEnergyConsumed = calculateTotalEnergyConsumed(device)

  // Only suggest if consumption exceeds the threshold
  if (totalEnergyConsumed < thresholds.energyThreshold) {
    return null
  }

  // Calculate potential savings (assume 20% reduction is possible)
  const potentialSaving = (totalEnergyConsumed * 0.2).toFixed(1) // kWh
  const costSaving = `${(Number.parseFloat(potentialSaving) * 0.45).toFixed(2)} AED` // Assuming 0.45 AED per kWh

  const template = suggestionTemplates.highConsumption
  const deviceName = device.name || deviceType.charAt(0).toUpperCase() + deviceType.slice(1)

  const suggestion: Suggestion = {
    title: template.title,
    description: template.description(deviceName, room, totalEnergyConsumed),
    icon: template.icon,
    iconColor: template.iconColor,
    saving: template.saving(Number.parseFloat(potentialSaving)),
    impact: template.impact(costSaving),
    action: template.action,
    category: template.category,
    details: [
      `Current consumption: ${totalEnergyConsumed.toFixed(1)} kWh this month`,
      `Average for ${deviceType}: ${thresholds.energyThreshold.toFixed(1)} kWh`,
      `Potential monthly savings: ${costSaving}`,
    ],
    deviceId: device.id,
  }

  return suggestion
}

function checkForPatterns(devices: Device[], room: string): Suggestion | null {
  // Group devices by type
  const deviceTypes = {}
  for (const device of devices) {
    if (!deviceTypes[device.type]) {
      deviceTypes[device.type] = []
    }
    deviceTypes[device.type].push(device)
  }

  // If there are multiple lights or climate control devices, suggest automation
  for (const [deviceType, typeDevices] of Object.entries(deviceTypes)) {
    if (typeDevices.length >= 2 && ["light", "thermostat", "fan"].includes(deviceType)) {
      const activeDevices = typeDevices.filter((d) => d.status === "on")
      if (activeDevices.length >= 2) {
        // Calculate potential savings (simplified)
        const totalPower = activeDevices.reduce((sum, d) => sum + getDevicePower(d), 0)
        const potentialSaving = ((totalPower * 2 * 30) / 1000).toFixed(1) // Assume 2 hours saved per day

        const template = suggestionTemplates.patternDetected
        const deviceName = deviceType.charAt(0).toUpperCase() + deviceType.slice(1) + "s"

        const suggestion: Suggestion = {
          title: template.title,
          description: template.description(deviceName, room),
          icon: template.icon,
          iconColor: template.iconColor,
          saving: template.saving(Number.parseFloat(potentialSaving)),
          impact: template.impact(),
          action: template.action,
          category: template.category,
          details: [
            `Pattern detected: Multiple ${deviceType}s used together`,
            `Affects: ${activeDevices.map((d) => d.name || `${deviceType} ${activeDevices.indexOf(d) + 1}`).join(", ")}`,
            `Suggested: Create a scene or automation`,
          ],
        }

        return suggestion
      }
    }
  }

  return null
}

function checkHighUsage(device: Device): Suggestion | null {
  const deviceType = device.type
  if (!deviceThresholds[deviceType]) {
    return null
  }

  // Calculate current usage
  const lastStatusChange = device.lastStatusChange || Date.now() - 3600000 * 6 // Default to 6 hours ago
  const now = Date.now()
  const hoursOn = (now - lastStatusChange) / (1000 * 60 * 60)

  // Only suggest if usage is significant and exceeds the threshold
  if (hoursOn < deviceThresholds[deviceType].usageThreshold) {
    return null
  }

  // Calculate potential savings
  const power = getDevicePower(device)
  const dailyUsage = deviceThresholds[deviceType]?.dailyUsageHours || 4

  // Assume 20% reduction is possible
  const potentialSaving = ((power * (hoursOn - dailyUsage) * 30) / 1000).toFixed(1) // kWh per month
  const costSaving = `${(Number.parseFloat(potentialSaving) * 0.45).toFixed(2)} AED` // Assuming 0.45 AED per kWh

  const template = suggestionTemplates.highUsage
  const deviceName = device.name || deviceType.charAt(0).toUpperCase() + deviceType.slice(1)
  const room = device.room || "Unknown"

  const suggestion: Suggestion = {
    title: template.title,
    description: template.description(deviceName, room, hoursOn),
    icon: template.icon,
    iconColor: template.iconColor,
    saving: template.saving(Number.parseFloat(potentialSaving)),
    impact: template.impact(costSaving),
    action: template.action,
    category: template.category,
    details: [
      `Current usage: ${hoursOn.toFixed(1)} hours today`,
      `Average usage: ${dailyUsage} hours per day`,
      `Potential monthly savings: ${costSaving}`,
    ],
    deviceId: device.id,
  }

  return suggestion
}

export async function POST(request: NextRequest) {
  try {
    const { devices, previousSuggestions } = await request.json()

    // Return immediately if no devices
    if (!devices || !Array.isArray(devices) || devices.length === 0) {
      return NextResponse.json({
        suggestions: [],
        noDevices: true,
        hasDevices: false,
        hasActiveSuggestions: false,
        hasNewSuggestions: false,
      })
    }

    // Generate suggestions
    const suggestions: Suggestion[] = []

    // Group devices by room for better analysis
    const rooms = {}
    for (const device of devices) {
      const room = device.room || "Unknown"
      if (!rooms[room]) {
        rooms[room] = []
      }
      rooms[room].push(device)
    }

    // Analyze each room
    for (const [room, roomDevices] of Object.entries(rooms)) {
      // Check for high settings (brightness, speed, etc.)
      for (const device of roomDevices) {
        if (device.status === "on") {
          // Check for high settings first
          const highSettingsSuggestion = checkHighSettings(device, room)
          if (highSettingsSuggestion) {
            suggestions.push(highSettingsSuggestion)
          }

          // Then check for excessive usage
          const excessiveUsageSuggestion = checkExcessiveUsage(device, room)
          if (excessiveUsageSuggestion) {
            suggestions.push(excessiveUsageSuggestion)
          }

          // Check for high usage
          const highUsageSuggestion = checkHighUsage(device)
          if (highUsageSuggestion) {
            suggestions.push(highUsageSuggestion)
          }
        }

        // Check for high consumption (regardless of current status)
        const highConsumptionSuggestion = checkHighConsumption(device, room)
        if (highConsumptionSuggestion) {
          suggestions.push(highConsumptionSuggestion)
        }
      }

      // Check for usage patterns that could be automated
      if (roomDevices.length >= 2) {
        const patternSuggestion = checkForPatterns(roomDevices, room)
        if (patternSuggestion) {
          suggestions.push(patternSuggestion)
        }
      }
    }

    // Check if there are new suggestions compared to stored ones
    const hasNewSuggestions =
      previousSuggestions && Array.isArray(previousSuggestions)
        ? suggestions.some((suggestion) => !previousSuggestions.some((stored) => stored.title === suggestion.title))
        : suggestions.length > 0

    // Add some randomization to make suggestions feel more dynamic
    if (suggestions.length > 5) {
      suggestions.sort(() => 0.5 - Math.random())
      suggestions.length = 5
    }

    console.log("Generated suggestions:", suggestions.length)

    return NextResponse.json({
      suggestions,
      hasDevices: true,
      hasActiveSuggestions: suggestions.length > 0,
      hasNewSuggestions:
        suggestions.length > 0 && (!previousSuggestions || suggestions.length > previousSuggestions.length),
      noDevices: false,
    })
  } catch (error) {
    console.error("Error in suggestions API:", error)

    // Return a proper error response that won't cause the client to hang
    return NextResponse.json(
      {
        error: "Failed to generate suggestions",
        suggestions: [],
        hasDevices: false,
        hasActiveSuggestions: false,
        hasNewSuggestions: false,
        noDevices: true,
      },
      { status: 500 },
    )
  }
}

