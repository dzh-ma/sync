import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from '@/components/ui/use-toast'

export function usePermission(requiredPermission: string) {
  const [hasPermission, setHasPermission] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const checkPermission = () => {
      setIsLoading(true)
      
      // Check for both currentUser (admin) and currentMember (household member)
      const storedUser = localStorage.getItem("currentUser")
      const storedMember = localStorage.getItem("currentMember")
      
      if (!storedUser && !storedMember) {
        router.push("/auth/login")
        return
      }
      
      let permissions = {}
      
      if (storedUser) {
        const currentUser = JSON.parse(storedUser)
        permissions = currentUser.permissions || {}
      } else if (storedMember) {
        const currentMember = JSON.parse(storedMember)
        permissions = currentMember.permissions || {}
      }
      
      const permitted = permissions[requiredPermission] === true
      
      setHasPermission(permitted)
      setIsLoading(false)
      
      if (!permitted) {
        toast({
          title: "Access Denied",
          description: `You don't have permission to access this feature.`,
          variant: "destructive",
        })
        router.push("/dashboard")
      }
    }
    
    checkPermission()
  }, [requiredPermission, router])
  
  return { hasPermission, isLoading }
} 