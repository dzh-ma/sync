// rooms/room-card.tsx
import Image from "next/image"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MoreVertical } from "lucide-react"

interface RoomCardProps {
  name: string
  image: string
}

export function RoomCard({ name, image }: RoomCardProps) {
  return (
    <Card className="overflow-hidden">
      <div className="relative aspect-video">
        <Image src={image || "/placeholder.svg"} alt={name} fill className="object-cover" />
        <div className="absolute top-2 right-2">
          <Button variant="ghost" size="icon" className="bg-white/80 hover:bg-white">
            <MoreVertical className="h-4 w-4" />
          </Button>
        </div>
        <div className="absolute bottom-2 left-2 bg-white/80 px-2 py-1 rounded text-sm">{name}</div>
      </div>
    </Card>
  )
}

