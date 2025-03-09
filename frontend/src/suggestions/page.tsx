"use client"

import React from "react"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card"
import { Button } from "../../components/ui/button"
import { Badge } from "../../components/ui/badge"
import { Download, User, Lightbulb, ThermometerSun, Timer, Fan, ArrowRight, Zap } from "lucide-react"
import { motion } from "framer-motion"
import { NavigationSidebar } from "../../components/navigation-sidebar";

const adminSuggestions = [
  {
    title: "Optimize Air Conditioning",
    description: "Your bedroom AC has been running continuously for 8 hours. Setting up a schedule could save energy.",
    icon: Fan,
    iconColor: "text-blue-500",
    saving: "Potential saving: 120 kWh/month",
    impact: "Environmental Impact: Reduce CO2 emissions by 60kg",
    action: "Setup Schedule",
    details: [
      "Current Usage: 8 hours continuous operation",
      "Recommended: 15-minute intervals with 2°C adjustment",
      "Peak hours detected: 2 PM - 5 PM",
    ],
    category: "Energy Efficiency",
  },
  {
    title: "Smart Lighting Pattern Detected",
    description: "We noticed regular lighting patterns in your living room. Would you like to automate this?",
    icon: Lightbulb,
    iconColor: "text-yellow-500",
    saving: "Potential saving: 45 kWh/month",
    impact: "Convenience: Automate daily routines",
    action: "Create Automation",
    details: [
      "Pattern detected: Lights on 6 PM - 11 PM",
      "Affects: Living Room, Kitchen",
      "Suggested: Gradual dimming by time",
    ],
    category: "Automation",
  },
  {
    title: "Temperature Optimization",
    description: "Your home's temperature varies significantly throughout the day. Let's optimize it.",
    icon: ThermometerSun,
    iconColor: "text-red-500",
    saving: "Potential saving: AED 150/month",
    impact: "Comfort: Maintain optimal temperature",
    action: "View Analysis",
    details: ["Current range: 19°C - 26°C", "Recommended: 23°C - 24°C", "Affected rooms: Bedroom, Living Room"],
    category: "Energy Efficiency",
  },
  {
    title: "Off-Peak Usage Opportunity",
    description: "Running your washing machine during off-peak hours could reduce your electricity bill.",
    icon: Timer,
    iconColor: "text-green-500",
    saving: "Potential saving: AED 80/month",
    impact: "Grid Impact: Reduce peak load stress",
    action: "See Off-Peak Hours",
    details: ["Peak hours: 2 PM - 6 PM", "Off-peak rates: 11 PM - 5 AM", "Applicable to: Washing Machine, Dishwasher"],
    category: "Cost Saving",
  },
]

const householdSuggestions = [
  {
    title: "Room Temperature Alert",
    description: "Your room temperature is set to 19°C. Consider increasing it to save energy.",
    icon: ThermometerSun,
    iconColor: "text-red-500",
    saving: "Potential saving: 30 kWh/month",
    impact: "Personal Comfort: Maintain optimal temperature",
    action: "Adjust Temperature",
    details: ["Current: 19°C", "Recommended: 23°C", "Energy usage: Above average"],
    category: "Energy Efficiency",
  },
  {
    title: "Lighting Reminder",
    description: "Lights in your room are often left on when you're away.",
    icon: Lightbulb,
    iconColor: "text-yellow-500",
    saving: "Potential saving: 15 kWh/month",
    impact: "Easy Fix: Use motion sensors",
    action: "Enable Auto-off",
    details: ["Pattern: Lights left on 2+ hours", "Suggestion: Enable motion detection", "Applies to: Your bedroom"],
    category: "Energy Efficiency",
  },
]

export default function SuggestionsPage() {
  const [suggestions, setSuggestions] = useState(adminSuggestions)
  const [userType, setUserType] = useState<"admin" | "household">("admin")

  useEffect(() => {
    const currentUser = JSON.parse(localStorage.getItem("currentUser") || '{"type": "admin"}')
    setUserType(currentUser.type)
    setSuggestions(currentUser.type === "admin" ? adminSuggestions : householdSuggestions)
  }, [])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
    },
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <NavigationSidebar /> {/* Add the navbar here */}
      <div className="ml-[72px]">
      <motion.div initial="hidden" animate="visible" variants={containerVariants} className="p-6">
        <motion.header variants={itemVariants} className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-[#00B2FF] to-[#0085FF] rounded-full flex items-center justify-center shadow-lg">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">Smart Suggestions</h1>
              <p className="text-sm text-gray-500">Optimize your home's energy usage</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              className="text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF] hover:text-white"
            >
              <Download className="h-5 w-5" />
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="text-[#00B2FF] border-[#00B2FF] hover:bg-[#00B2FF] hover:text-white"
            >
              <User className="h-5 w-5" />
            </Button>
          </div>
        </motion.header>

        <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {suggestions.map((suggestion, index) => (
            <motion.div key={suggestion.title} variants={itemVariants}>
              <Card className="overflow-hidden hover:shadow-lg transition-shadow duration-300">
                <CardHeader className="bg-gradient-to-r from-[#00B2FF] to-[#0085FF] pb-8 relative">
                  <CardTitle className="text-white text-xl mb-2">{suggestion.title}</CardTitle>
                  <p className="text-white/80 text-sm">{suggestion.description}</p>
                  <div className="absolute bottom-0 right-0 transform translate-y-1/2 mr-6">
                    <div className="w-12 h-12 rounded-full bg-white flex items-center justify-center shadow-lg">
                      <suggestion.icon className={`w-6 h-6 ${suggestion.iconColor}`} />
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-8">
                  <div className="space-y-4">
                    <div>
                      <Badge variant="secondary" className="mb-2">
                        {suggestion.category}
                      </Badge>
                      <p className="text-sm font-medium text-green-600">{suggestion.saving}</p>
                      <p className="text-sm text-gray-600">{suggestion.impact}</p>
                    </div>
                    <div className="space-y-2">
                      {suggestion.details.map((detail, idx) => (
                        <div key={idx} className="flex items-center text-sm text-gray-600">
                          <div className="w-1.5 h-1.5 rounded-full bg-[#00B2FF] mr-2" />
                          {detail}
                        </div>
                      ))}
                    </div>
                    <Button className="w-full bg-[#00B2FF] hover:bg-[#00B2FF]/90">
                      {suggestion.action}
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
        </div>
    </div>
  )
}
