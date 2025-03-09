"use client"

import { useNavigate } from "react-router-dom"

export function useLogout() {
  const navigate = useNavigate()

  return () => {
    // Instead of removing the user, we'll just redirect to the dashboard
    navigate("/auth/login")
  }
}

