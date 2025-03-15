import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"

export function FamilyMembers() {
  return (
    <div className="bg-white rounded-xl p-4 mt-4">
      <h3 className="font-medium mb-4">Family Members</h3>
      <div className="space-y-4">
        {[
          { name: "You", role: "House Manager" },
          { name: "Olivia", role: "House Member" },
          { name: "Noah", role: "Child" },
          { name: "Ben", role: "House Member" },
        ].map((member) => (
          <div key={member.name} className="flex items-center">
            <Avatar className="h-10 w-10">
              <AvatarImage src="/placeholder.svg" />
              <AvatarFallback>{member.name[0]}</AvatarFallback>
            </Avatar>
            <div className="ml-3 flex-1">
              <div className="font-medium">{member.name}</div>
              <div className="text-sm text-muted-foreground">{member.role}</div>
            </div>
            <Button variant="outline" size="sm" className="ml-auto">
              Manage Profile
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
}

