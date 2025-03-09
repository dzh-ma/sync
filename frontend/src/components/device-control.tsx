"use client"

import React from "react"
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/card"
import { Switch } from "../../components/ui/switch"
import { Slider } from "../../components/ui/slider"
import { Label } from "../../components/ui/label"
import { Lightbulb, Thermometer, Wind } from "lucide-react"
import './DeviceControl.module.css'; // Import the CSS file

interface DeviceControlProps {
  room: string
}

export function DeviceControl({ room }: DeviceControlProps) {
  return (
    <Card className="card-containerD">
      <CardHeader className="card-headerD">
        <CardTitle className="card-titleD">{room} Devices</CardTitle>
      </CardHeader>
      <CardContent className="card-contentD space-y-4">
        <div className="device-control-itemD">
          <div className="flex items-center space-x-2">
            <Lightbulb className="iconD" />
            <Label htmlFor="lights" className="labelD">Lights</Label>
          </div>
          <Switch id="lights" />
        </div>

        <div className="space-y-2">
          <div className="temperature-slider-containerD">
            <div className="flex items-center space-x-2">
              <Thermometer className="iconD" />
              <Label htmlFor="temperature" className="labelD">Temperature</Label>
            </div>
            <span>22°C</span>
          </div>
          <Slider id="temperature" min={16} max={30} step={1} defaultValue={[22]} className="sliderD" />
        </div>

        <div className="device-control-itemD">
          <div className="flex items-center space-x-2">
            <Wind className="iconD" />
            <Label htmlFor="ac" className="labelD">Air Conditioning</Label>
          </div>
          <Switch id="ac" />
        </div>
      </CardContent>
    </Card>
  )
}
