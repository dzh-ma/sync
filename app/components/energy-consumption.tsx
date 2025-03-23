"use client"

import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { LineChart } from "@/components/charts"
import './EnergyConsumption.module.css' // Import the CSS file

interface EnergyData {
  date: string
  usage: number
}

export function EnergyConsumption() {
  const [timeframe, setTimeframe] = useState("week")
  const [energyData, setEnergyData] = useState<EnergyData[]>([])
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    // Mark component as mounted on client side
    setIsMounted(true)
    
    // In a real application, this would fetch data from an API
    const generateData = () => {
      const data: EnergyData[] = []
      const now = new Date()
      const daysToGenerate = timeframe === "week" ? 7 : 30

      for (let i = daysToGenerate - 1; i >= 0; i--) {
        const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000)
        data.push({
          date: date.toISOString().split("T")[0],
          usage: Math.floor(Math.random() * 20) + 10, // Random usage between 10 and 30 kWh
        })
      }

      setEnergyData(data)
    }

    generateData()
  }, [timeframe])

  // Safely format the chart data to prevent objects being passed as React children
  const getChartData = () => {
    return energyData.map((d) => ({
      name: d.date,
      usage: d.usage
    }))
  }

  // Only render chart when component is mounted on client
  if (!isMounted) {
    return (
      <Card className="card-container-E">
        <CardHeader className="card-header-E">
          <CardTitle className="card-title-E">Energy Consumption</CardTitle>
        </CardHeader>
        <CardContent className="card-content-E">
          <div className="flex items-center justify-center p-6">
            <p className="text-sm text-gray-500">Loading energy data...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="card-container-E">
      <CardHeader className="card-header-E">
        <CardTitle className="card-title-E">Energy Consumption</CardTitle>
        <Select value={timeframe} onValueChange={(value) => setTimeframe(value)}>
          <SelectTrigger className="select-trigger-E">
            <SelectValue placeholder="Select timeframe" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="week">Last Week</SelectItem>
            <SelectItem value="month">Last Month</SelectItem>
          </SelectContent>
        </Select>
      </CardHeader>
      <CardContent className="card-content-E">
        {energyData.length > 0 ? (
          <LineChart
            data={getChartData()}
            xAxisLabel="Date"
            yAxisLabel="Energy (kWh)"
          />
        ) : (
          <div className="flex items-center justify-center p-6">
            <p className="text-sm text-gray-500">No energy data available</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
