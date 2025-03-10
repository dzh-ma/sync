import React from "react"
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/card"
import { Button } from "../../components/ui/button"
import { Sun, Moon, Coffee, Tv, Book, DoorClosed } from "lucide-react"

const scenes = [
  { name: "Good Morning", icon: Sun, color: "bg-yellow-500" },
  { name: "Good Night", icon: Moon, color: "bg-blue-500" },
  { name: "Movie Time", icon: Tv, color: "bg-purple-500" },
  { name: "Reading Mode", icon: Book, color: "bg-green-500" },
  { name: "Coffee Break", icon: Coffee, color: "bg-orange-500" },
  { name: "Away Mode", icon: DoorClosed, color: "bg-red-500" },
]

export function SmartScenes() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Smart Scenes</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3">
          {scenes.map((scene) => (
            <Button key={scene.name} variant="outline" className="h-auto py-4 flex flex-col items-center gap-2">
              <div className={`p-2 rounded-full ${scene.color}`}>
                <scene.icon className="h-5 w-5 text-white" />
              </div>
              <span className="text-sm">{scene.name}</span>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

