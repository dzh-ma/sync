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

  useEffect(() => {
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
        <LineChart
          data={energyData.map((d) => ({ name: d.date, usage: d.usage }))}
          xAxisLabel="Date"
          yAxisLabel="Energy (kWh)"
        />
      </CardContent>
    </Card>
  )
}
