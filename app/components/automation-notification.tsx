"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Zap, X } from "lucide-react"

interface NotificationProps {
  message: string
  onClose: () => void
}

export function AutomationNotification({ message, onClose }: NotificationProps) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(onClose, 300) // Allow animation to complete before removing
    }, 5000)

    return () => clearTimeout(timer)
  }, [onClose])

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -50, x: "-50%" }}
          animate={{ opacity: 1, y: 0, x: "-50%" }}
          exit={{ opacity: 0, y: -50, x: "-50%" }}
          className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 bg-white rounded-lg shadow-lg p-4 flex items-center gap-3 max-w-md"
        >
          <div className="bg-blue-100 p-2 rounded-full">
            <Zap className="h-5 w-5 text-blue-600" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-800">{message}</p>
          </div>
          <button onClick={() => setIsVisible(false)} className="text-gray-400 hover:text-gray-600">
            <X className="h-4 w-4" />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  )
} 