"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { LineChart } from "@/components/charts"
import { Battery, BatteryCharging, Clock, Zap } from "lucide-react"

interface EnergyUsageWidgetProps {
  data: {
    daily: { name: string; usage: number }[]
    weekly: { name: string; usage: number }[]
    monthly: { name: string; usage: number }[]
  }
}

export function EnergyUsageWidget({ data }: EnergyUsageWidgetProps) {
  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-medium flex items-center">
          <Zap className="h-5 w-5 mr-2 text-[#00B2FF]" />
          Energy Usage
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="daily" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-4">
            <TabsTrigger value="daily">Daily</TabsTrigger>
            <TabsTrigger value="weekly">Weekly</TabsTrigger>
            <TabsTrigger value="monthly">Monthly</TabsTrigger>
          </TabsList>
          <div className="w-full overflow-hidden">
            <TabsContent value="daily" className="h-[300px] w-full">
              <div className="w-full h-full">
                <LineChart data={data.daily} />
              </div>
              <div className="flex justify-between mt-4 text-sm">
                <div className="flex items-center">
                  <Battery className="h-4 w-4 mr-1 text-green-500" />
                  <span>Peak: 4.2 kWh</span>
                </div>
                <div className="flex items-center">
                  <BatteryCharging className="h-4 w-4 mr-1 text-amber-500" />
                  <span>Avg: 2.8 kWh</span>
                </div>
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-1 text-blue-500" />
                  <span>Off-peak savings: 15%</span>
                </div>
              </div>
            </TabsContent>
            <TabsContent value="weekly" className="h-[300px] w-full">
              <div className="w-full h-full">
                <LineChart data={data.weekly} />
              </div>
              <div className="flex justify-between mt-4 text-sm">
                <div className="flex items-center">
                  <Battery className="h-4 w-4 mr-1 text-green-500" />
                  <span>Peak: 28.5 kWh</span>
                </div>
                <div className="flex items-center">
                  <BatteryCharging className="h-4 w-4 mr-1 text-amber-500" />
                  <span>Avg: 19.6 kWh</span>
                </div>
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-1 text-blue-500" />
                  <span>Off-peak savings: 18%</span>
                </div>
              </div>
            </TabsContent>
            <TabsContent value="monthly" className="h-[300px] w-full">
              <div className="w-full h-full">
                <LineChart data={data.monthly} />
              </div>
              <div className="flex justify-between mt-4 text-sm">
                <div className="flex items-center">
                  <Battery className="h-4 w-4 mr-1 text-green-500" />
                  <span>Peak: 120 kWh</span>
                </div>
                <div className="flex items-center">
                  <BatteryCharging className="h-4 w-4 mr-1 text-amber-500" />
                  <span>Avg: 85 kWh</span>
                </div>
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-1 text-blue-500" />
                  <span>Off-peak savings: 22%</span>
                </div>
              </div>
            </TabsContent>
          </div>
        </Tabs>
      </CardContent>
    </Card>
  )
}

