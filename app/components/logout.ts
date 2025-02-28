"use client"

import { useRouter } from "next/navigation"

export function useLogout() {
  const router = useRouter()

  return () => {
    // Instead of removing the user, we'll just redirect to the dashboard
    router.push("/auth/login")
  }
}

