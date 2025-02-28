import { Button } from "@/components/ui/button"
import { ChevronRight } from "lucide-react"

const rooms = ["Living Room", "Bedroom", "Corridor", "Kitchen", "Garage", "Play Area"]

export function RoomSelector() {
  return (
    <div className="flex items-center space-x-2 overflow-x-auto py-2">
      {rooms.map((room, index) => (
        <Button
          key={room}
          variant={index === 0 ? "default" : "ghost"}
          className={index === 0 ? "bg-[#00B2FF] hover:bg-[#00B2FF]/90" : ""}
        >
          {room}
        </Button>
      ))}
      <Button variant="ghost" size="icon">
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  )
}

