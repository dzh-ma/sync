import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Sun, Cloud, Droplets } from "lucide-react"

export function WeatherWidget() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Weather</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sun className="h-8 w-8 text-yellow-500" />
            <div>
              <p className="text-2xl font-bold">28°C</p>
              <p className="text-sm text-gray-500">Sunny</p>
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-1">
              <Cloud className="h-4 w-4" />
              <span className="text-sm">20%</span>
            </div>
            <div className="flex items-center space-x-1">
              <Droplets className="h-4 w-4" />
              <span className="text-sm">30%</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

