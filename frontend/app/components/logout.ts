"use client"

import { useRouter } from "next/navigation"

export function useLogout() {
  const router = useRouter()

  return () => {
    // Clear localStorage items
    localStorage.removeItem('currentUser');
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    
    // Use the correct path
    router.push("/auth/login")
  }
}
