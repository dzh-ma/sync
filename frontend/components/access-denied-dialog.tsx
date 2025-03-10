import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Lock } from "lucide-react"
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

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Access Required</DialogTitle>
          <DialogDescription>You don't have permission to access {featureName}.</DialogDescription>
        </DialogHeader>
        <div className="flex flex-col items-center justify-center p-4">
          <Lock className="w-12 h-12 text-gray-400 mb-4" />
          <Button onClick={handleRequestAccess}>Request Access</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

