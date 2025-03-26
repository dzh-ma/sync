"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Cloud, CloudRain, Sun, Thermometer, Wind, Zap, RefreshCw } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import axios from "axios"

interface WeatherData {
  city: string
  temperature: number
  condition: "sunny" | "cloudy" | "rainy" | "windy"
  description: string
  humidity: number
  windSpeed: number
  icon: string
  units: string
  timestamp: string
}

interface WeatherEnergyWidgetProps {
  city?: string
  units?: "metric" | "imperial"
}

export function WeatherEnergyWidget({ city = "Dubai", units = "metric" }: WeatherEnergyWidgetProps) {
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null)
  const [loading, setLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchWeatherData = async () => {
    try {
      setIsRefreshing(true)
      const timestamp = new Date().getTime() // Add timestamp to prevent caching
      const response = await axios.get(`/api/weather?city=${encodeURIComponent(city)}&units=${units}&_t=${timestamp}`)
      setWeatherData(response.data)
      setError(null)
    } catch (err) {
      console.error("Error fetching weather data:", err)
      setError("Could not load weather data")
    } finally {
      setLoading(false)
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    fetchWeatherData()

    // Refresh weather data every 30 minutes
    const intervalId = setInterval(fetchWeatherData, 30 * 60 * 1000)
    
    return () => clearInterval(intervalId)
  }, [city, units])

  const handleRefresh = () => {
    fetchWeatherData()
  }

  const getWeatherIcon = () => {
    if (!weatherData) {
      return <Cloud className="h-10 w-10 text-gray-300" />
    }

    switch (weatherData.condition) {
      case "sunny":
        return <Sun className="h-10 w-10 text-yellow-500" />
      case "cloudy":
        return <Cloud className="h-10 w-10 text-gray-500" />
      case "rainy":
        return <CloudRain className="h-10 w-10 text-blue-500" />
      case "windy":
        return <Wind className="h-10 w-10 text-blue-300" />
      default:
        return <Sun className="h-10 w-10 text-yellow-500" />
    }
  }

  const getEnergyTip = () => {
    if (!weatherData) return "Adjust your thermostat to save energy."

    switch (weatherData.condition) {
      case "sunny":
        return "Perfect day to air-dry laundry instead of using the dryer."
      case "cloudy":
        return "Use natural light where possible to reduce lighting costs."
      case "rainy":
        return "Good day to run your dishwasher and washing machine (full loads)."
      case "windy":
        return "Open windows for natural cooling instead of using AC."
      default:
        return "Adjust your thermostat to save energy."
    }
  }

  const getOptimalACTemp = () => {
    if (!weatherData) return units === "metric" ? "23°C" : "74°F"
    
    // Calculate optimal AC temperature based on outside temperature
    let optimalTemp = 0
    if (units === "metric") {
      // For Celsius
      optimalTemp = weatherData.temperature > 30 ? 24 : 23
      return `${optimalTemp}°C`
    } else {
      // For Fahrenheit
      optimalTemp = weatherData.temperature > 86 ? 75 : 74
      return `${optimalTemp}°F`
    }
  }
  
  // Show loading state
  if (loading) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-medium">Weather & Energy</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-6">
            <div className="animate-pulse flex flex-col items-center">
              <div className="rounded-full bg-gray-200 h-10 w-10 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-24 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-16"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Show error state
  if (error) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-medium">Weather & Energy</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-4">
            <p className="text-red-500 text-sm">{error}</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Default to empty data if weather data is null
  const temperature = weatherData?.temperature ?? 0
  const condition = weatherData?.condition ?? "sunny"
  const humidity = weatherData?.humidity ?? 0
  const windSpeed = weatherData?.windSpeed ?? 0
  const cityName = weatherData?.city ?? city
  const tempUnit = units === "metric" ? "°C" : "°F"
  const speedUnit = units === "metric" ? "km/h" : "mph"

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-medium flex justify-between items-center">
          Weather & Energy
          <Button 
            variant="ghost" 
            size="sm" 
            className="h-8 w-8 p-0"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            <RefreshCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span className="sr-only">Refresh</span>
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            {getWeatherIcon()}
            <div className="ml-4">
              <div className="text-2xl font-bold">{temperature}{tempUnit}</div>
              <div className="text-sm text-gray-500 capitalize">
                {weatherData?.description || condition} in {cityName}
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="flex items-center justify-end mb-1">
              <Thermometer className="h-4 w-4 mr-1 text-red-500" />
              <span className="text-sm">{humidity}% humidity</span>
            </div>
            <div className="flex items-center justify-end">
              <Wind className="h-4 w-4 mr-1 text-blue-500" />
              <span className="text-sm">{windSpeed} {speedUnit}</span>
            </div>
          </div>
        </div>

        <div className="mt-4 bg-blue-50 p-3 rounded-md">
          <div className="flex items-start">
            <div className="bg-blue-100 p-1.5 rounded-full">
              <Zap className="h-4 w-4 text-blue-600" />
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-blue-800">Today's Energy Tip</h4>
              <p className="text-xs text-blue-700 mt-0.5">{getEnergyTip()}</p>
            </div>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <Badge variant="outline" className="bg-green-50 text-green-700 hover:bg-green-100">
            Optimal AC: {getOptimalACTemp()}
          </Badge>
          <Badge variant="outline" className="bg-blue-50 text-blue-700 hover:bg-blue-100">
            Peak Hours: 2-6pm
          </Badge>
          <Badge variant="outline" className="bg-amber-50 text-amber-700 hover:bg-amber-100">
            Savings Potential: High
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}

