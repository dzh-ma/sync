import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Lock, ShieldAlert } from "lucide-react"
import { useToast } from "@/components/ui/use-toast"

interface AccessDeniedDialogProps {
  isOpen: boolean
  onClose: () => void
  featureName: string
}

export function AccessDeniedDialog({ isOpen, onClose, featureName }: AccessDeniedDialogProps) {
  const { toast } = useToast()

  const handleRequestAccess = () => {
    toast({
      title: "Access Requested",
      description: `Your request for access to ${featureName} has been sent to the admin.`,
    })
    onClose()
  }

  // Get helpful message based on feature name
  const getHelpMessage = () => {
    switch (featureName) {
      case "Automations":
        return "Automations allow you to create scheduled routines for your smart devices."
      case "Devices":
        return "Device control lets you manage the status of your smart home devices."
      case "Add Room":
        return "Adding rooms helps organize your smart home devices by location."
      default:
        return "This feature requires special permissions granted by your household admin."
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-amber-500" />
            <DialogTitle>Access Required</DialogTitle>
          </div>
          <DialogDescription>
            You don't have permission to access {featureName}.
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col items-center justify-center py-4">
          <Lock className="w-16 h-16 text-gray-300 mb-4" />
          <p className="text-center text-sm text-gray-500 mb-2">
            {getHelpMessage()}
          </p>
          <p className="text-center text-xs text-gray-400 mb-4">
            Contact your household admin or request access below.
          </p>
        </div>
        <DialogFooter className="sm:justify-between">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleRequestAccess} className="bg-[#FF9500] hover:bg-[#FF9500]/90">
            Request Access
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

