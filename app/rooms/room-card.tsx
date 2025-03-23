import Image from "next/image"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { MoreVertical, Trash2 } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface RoomCardProps {
  id: string;
  name: string;
  type: string;
  image: string;
  onDelete: (id: string) => void;
}

export function RoomCard({ id, name, type, image, onDelete }: RoomCardProps) {
  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete the room "${name}"?`)) {
      onDelete(id);
    }
  };

  // Function to get a readable room type
  const getRoomTypeLabel = (type: string) => {
    const typeMap: Record<string, string> = {
      living: "Living Room",
      bedroom: "Bedroom",
      kitchen: "Kitchen",
      bathroom: "Bathroom",
      office: "Office",
      garage: "Garage"
    };
    
    return typeMap[type] || type;
  };

  return (
    <Card className="overflow-hidden">
      <div className="relative aspect-video">
        <Image src={image || "/placeholder.svg"} alt={name} fill className="object-cover" />
        <div className="absolute top-2 right-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="bg-white/80 hover:bg-white">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleDelete} className="text-red-500">
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-3">
          <h3 className="text-white font-medium">{name}</h3>
          <p className="text-white/80 text-sm">{getRoomTypeLabel(type)}</p>
        </div>
      </div>
    </Card>
  )
}

