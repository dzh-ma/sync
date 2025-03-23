"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { Mic } from "lucide-react"
import { Button } from "@/components/ui/button"
import { motion, AnimatePresence } from "framer-motion"

interface VoiceAssistantProps {
  devices: any[]
  rooms: any[]
  toggleDevice: (deviceId: string, status: boolean) => void
}

export function VoiceAssistant({ devices, rooms, toggleDevice }: VoiceAssistantProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState("")
  const [feedback, setFeedback] = useState("")
  const [showFeedback, setShowFeedback] = useState(false)
  const [permissionError, setPermissionError] = useState(false)
  const recognitionRef = useRef<any>(null)
  const router = useRouter()

  // Initialize speech recognition
  useEffect(() => {
    // Make sure we're in a browser environment
    if (typeof window === "undefined") return

    // Define the SpeechRecognition constructor
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

    // Check if speech recognition is available
    if (!SpeechRecognition) {
      console.error("Speech Recognition API is not supported in this browser")
      return
    }

    // Create a new recognition instance
    try {
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = "en-US"

      // Set up event handlers
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript.toLowerCase()
        console.log("Recognized speech:", transcript)
        setTranscript(transcript)
        handleCommand(transcript)
      }

      recognitionRef.current.onend = () => {
        console.log("Speech recognition ended")
        setIsListening(false)
      }

      recognitionRef.current.onerror = (event) => {
        console.error("Speech recognition error:", event.error)

        if (event.error === "not-allowed" || event.error === "permission-denied") {
          setPermissionError(true)
          setFeedback("Please allow microphone access to use voice commands.")
        } else {
          setFeedback(`Error: ${event.error}. Please try again.`)
        }

        setShowFeedback(true)
        setIsListening(false)
      }

      console.log("Speech recognition initialized successfully")
    } catch (error) {
      console.error("Error initializing speech recognition:", error)
    }

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort()
        } catch (error) {
          console.error("Error stopping speech recognition:", error)
        }
      }
    }
  }, [])

  const openAssistant = () => {
    setIsOpen(true)
    setTranscript("")
    setFeedback("")
    setShowFeedback(false)
    setPermissionError(false)
    setIsListening(true)

    // Start listening after a short delay to allow the animation to complete
    setTimeout(() => {
      startListening()
    }, 300)
  }

  const closeAssistant = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort()
      } catch (error) {
        console.error("Error stopping speech recognition:", error)
      }
    }
    setIsListening(false)
    setIsOpen(false)
  }

  const startListening = () => {
    // Check if speech recognition is available
    if (!recognitionRef.current) {
      console.error("Speech recognition not available")
      setFeedback("Speech recognition is not supported in your browser. Please try using Chrome, Edge, or Safari.")
      setShowFeedback(true)
      return
    }

    try {
      console.log("Starting speech recognition...")
      recognitionRef.current.start()
      setIsListening(true)
    } catch (error) {
      console.error("Error starting speech recognition:", error)
      setFeedback("Could not start listening. Please try again.")
      setShowFeedback(true)
    }
  }

  const handleCommand = (command: string) => {
    // Navigation commands - can redirect to any page
    if (
      command.includes("go to") ||
      command.includes("show") ||
      command.includes("open") ||
      command.includes("take me to")
    ) {
      // Extract the destination from the command
      let destination = ""

      // UPDATED: "rooms" now redirects to "/add-room" as requested
      if (command.includes("room")) {
        destination = "/add-room" // Changed from "/rooms" to "/add-room"
        setFeedback("Taking you to add room...")
      } else if (command.includes("device")) {
        destination = "/devices"
        setFeedback("Taking you to devices...")
      } else if (command.includes("dashboard") || command.includes("home")) {
        destination = "/dashboard"
        setFeedback("Taking you to dashboard...")
      } else if (command.includes("suggestion") || command.includes("tip")) {
        destination = "/suggestions"
        setFeedback("Taking you to suggestions...")
      } else if (command.includes("automation")) {
        destination = "/automations"
        setFeedback("Taking you to automations...")
      } else if (command.includes("profile")) {
        destination = "/profile"
        setFeedback("Taking you to profile...")
      } else if (command.includes("setting")) {
        destination = "/settings"
        setFeedback("Taking you to settings...")
      } else if (command.includes("statistic") || command.includes("stat")) {
        destination = "/statistics"
        setFeedback("Taking you to statistics...")
      } else {
        setFeedback("I'm not sure which page you want to go to.")
        setShowFeedback(true)
        return
      }

      setShowFeedback(true)
      setTimeout(() => {
        router.push(destination)
        setIsOpen(false)
      }, 1500)
      return
    }

    // Add commands - these are now redundant since "go to rooms" will take to add-room
    // but keeping for clarity and alternative phrasings
    if (command.includes("add room") || command.includes("create room") || command.includes("new room")) {
      setFeedback("Taking you to add room...")
      setShowFeedback(true)
      setTimeout(() => {
        router.push("/add-room")
        setIsOpen(false)
      }, 1500)
      return
    }

    if (command.includes("add device") || command.includes("create device") || command.includes("new device")) {
      setFeedback("Taking you to add device...")
      setShowFeedback(true)
      setTimeout(() => {
        router.push("/add-device")
        setIsOpen(false)
      }, 1500)
      return
    }

    // Device control commands - can control any device
    if (command.includes("turn on") || command.includes("switch on") || command.includes("enable")) {
      const deviceName = command.replace(/turn on|switch on|enable/gi, "").trim()
      const device = findDevice(deviceName)

      if (device) {
        toggleDevice(device.id, true)
        setFeedback(`Turning on ${device.name}...`)
        setShowFeedback(true)
        setTimeout(() => {
          setIsOpen(false)
        }, 1500)
      } else {
        setFeedback(`I couldn't find a device called "${deviceName}". Please try again.`)
        setShowFeedback(true)
      }
      return
    }

    if (command.includes("turn off") || command.includes("switch off") || command.includes("disable")) {
      const deviceName = command.replace(/turn off|switch off|disable/gi, "").trim()
      const device = findDevice(deviceName)

      if (device) {
        toggleDevice(device.id, false)
        setFeedback(`Turning off ${device.name}...`)
        setShowFeedback(true)
        setTimeout(() => {
          setIsOpen(false)
        }, 1500)
      } else {
        setFeedback(`I couldn't find a device called "${deviceName}". Please try again.`)
        setShowFeedback(true)
      }
      return
    }

    // Help command
    if (command.includes("help") || command.includes("what can you do")) {
      setFeedback(
        "I can help you navigate to any page or control your devices. Try saying 'go to rooms', 'open settings', 'turn on living room light', or 'turn off kitchen fan'.",
      )
      setShowFeedback(true)
      return
    }

    // If no command matched
    setFeedback("I'm not sure what you want me to do. Try saying 'help' for assistance.")
    setShowFeedback(true)
  }

  // Find any device by name, room, or type
  const findDevice = (deviceName: string) => {
    return devices.find(
      (device) =>
        device.name.toLowerCase().includes(deviceName) ||
        (device.room.toLowerCase() + " " + device.type.toLowerCase()).includes(deviceName),
    )
  }

  return (
    <>
      <Button
        onClick={openAssistant}
        className="rounded-full w-12 h-12 flex items-center justify-center bg-[#00B2FF] hover:bg-[#00B2FF]/90"
        aria-label="Voice assistant"
      >
        <Mic className="h-5 w-5" />
      </Button>

      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 flex items-center justify-center z-50">
            {/* Backdrop with blur effect */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/30 backdrop-blur-sm"
              onClick={closeAssistant}
            />

            {/* Simplified centered voice assistant modal - matching the screenshot */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ type: "spring", damping: 25, stiffness: 300 }}
              className="relative z-10 bg-white rounded-lg shadow-xl w-[400px] max-w-[90vw] overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-8 flex flex-col items-center justify-center">
                {/* Microphone circle */}
                <div className="w-24 h-24 rounded-full bg-red-100 flex items-center justify-center mb-4">
                  <Mic className="h-10 w-10 text-red-500" />
                </div>

                {/* Status text */}
                <h3 className="text-xl font-medium text-center mb-6">Listening...</h3>

                {/* Transcript - only show if we have one */}
                {transcript && (
                  <div className="w-full mb-4">
                    <p className="text-sm text-gray-700 text-center">"{transcript}"</p>
                  </div>
                )}

                {/* Feedback - only show if we have feedback */}
                {showFeedback && (
                  <div className="w-full mb-4">
                    <p className="text-sm text-blue-600 text-center">{feedback}</p>
                  </div>
                )}

                {/* Cancel button */}
                <Button variant="outline" onClick={closeAssistant} className="mt-2 min-w-[100px]">
                  Cancel
                </Button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  )
}

