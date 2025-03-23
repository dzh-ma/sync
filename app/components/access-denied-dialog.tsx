import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Lock } from "lucide-react"

interface AccessDeniedDialogProps {
  isOpen: boolean
  onClose: () => void
  featureName: string
}

export function AccessDeniedDialog({ isOpen, onClose, featureName }: AccessDeniedDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader className="flex flex-col items-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <Lock className="h-8 w-8 text-red-500" />
          </div>
          <DialogTitle>Access Denied</DialogTitle>
          <DialogDescription className="text-center pt-2">
            You don't have permission to access {featureName}. Please contact your household admin for access.
          </DialogDescription>
        </DialogHeader>
        <div className="flex justify-center pt-4">
          <Button onClick={onClose}>Close</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
} 