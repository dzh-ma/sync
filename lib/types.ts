export interface Device {
  id: string
  name: string
  type: string
  room: string
  status: "on" | "off"
  brightness?: number
  temperature?: number
  speed?: number
  lastStatusChange?: number
  powerConsumption: number
  totalEnergyConsumed: number
  usageHistory?: {
    startTime: number
    endTime?: number
    powerConsumption: number
    energyConsumed: number
  }[]
}

export interface Suggestion {
  title: string
  description: string
  icon: string
  iconColor: string
  saving: string
  impact?: string
  action?: string
  details?: string[]
  category?: string
  deviceId?: string
} 