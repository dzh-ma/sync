"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Sun, Moon, Home, Clock, Plus } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import styles from './AutomationWidget.module.css'

interface Automation {
  id: number
  name: string
  description: string
  icon: string
  active: boolean
  schedule: string
  type: string
}

const automationIcons: Record<string, any> = {
  Sun,
  Moon,
  Home,
  Clock,
}

export function AutomationWidget() {
  const [automations, setAutomations] = useState<Automation[]>([])
  const [newAutomation, setNewAutomation] = useState({
    name: "",
    description: "",
    icon: "Clock",
    schedule: "",
    type: "",
  })

  useEffect(() => {
    const storedAutomations = JSON.parse(localStorage.getItem("automations") || "[]")
    setAutomations(storedAutomations)
  }, [])

  const toggleAutomation = (id: number) => {
    const updatedAutomations = automations.map((automation) =>
      automation.id === id ? { ...automation, active: !automation.active } : automation,
    )
    setAutomations(updatedAutomations)
    localStorage.setItem("automations", JSON.stringify(updatedAutomations))
  }

  const addAutomation = () => {
    const newAutomationItem = {
      id: Date.now(),
      ...newAutomation,
      active: true,
    }
    const updatedAutomations = [...automations, newAutomationItem]
    setAutomations(updatedAutomations)
    localStorage.setItem("automations", JSON.stringify(updatedAutomations))
    setNewAutomation({
      name: "",
      description: "",
      icon: "Clock",
      schedule: "",
      type: "",
    })
  }

  return (
    <Card className={styles.cardAuto}>
      <CardHeader className={styles.cardHeaderAuto}>
        <CardTitle className={styles.cardTitleAuto}>Automations</CardTitle>
        <Dialog>
          <DialogTrigger asChild>
            <Button variant="outline" size="icon">
              <Plus className="h-4 w-4" />
            </Button>
          </DialogTrigger>
          <DialogContent className={styles.dialogContentAuto}>
            <DialogHeader>
              <DialogTitle>Create New Automation</DialogTitle>
              <DialogDescription>Set up a new automation for your smart home.</DialogDescription>
            </DialogHeader>
            <div className={styles.gridContainerAuto}>
              <div className={styles.gridItemAuto}>
                <Label htmlFor="name" className="text-left">
                  Name
                </Label>
                <Input
                  id="name"
                  value={newAutomation.name}
                  onChange={(e) => setNewAutomation({ ...newAutomation, name: e.target.value })}
                  className="col-span-3"
                />
              </div>
              <div className={styles.gridItemAuto}>
                <Label htmlFor="description" className="text-left">
                  Description
                </Label>
                <Input
                  id="description"
                  value={newAutomation.description}
                  onChange={(e) => setNewAutomation({ ...newAutomation, description: e.target.value })}
                  className="col-span-3"
                />
              </div>
              <div className={styles.gridItemAuto}>
                <Label htmlFor="icon" className="text-left">
                  Icon
                </Label>
                <Select
                  value={newAutomation.icon}
                  onValueChange={(value) => setNewAutomation({ ...newAutomation, icon: value })}
                >
                  <SelectTrigger className="col-span-3">
                    <SelectValue placeholder="Select icon" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Sun">Sun</SelectItem>
                    <SelectItem value="Moon">Moon</SelectItem>
                    <SelectItem value="Home">Home</SelectItem>
                    <SelectItem value="Clock">Clock</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className={styles.gridItemAuto}>
                <Label htmlFor="schedule" className="text-left">
                  Schedule
                </Label>
                <Input
                  id="schedule"
                  value={newAutomation.schedule}
                  onChange={(e) => setNewAutomation({ ...newAutomation, schedule: e.target.value })}
                  className="col-span-3"
                  placeholder="e.g., Daily at 8:00 AM"
                />
              </div>
              <div className={styles.gridItemAuto}>
                <Label htmlFor="type" className="text-left">
                  Type
                </Label>
                <Select
                  value={newAutomation.type}
                  onValueChange={(value) => setNewAutomation({ ...newAutomation, type: value })}
                >
                  <SelectTrigger className="col-span-3">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Time-based">Time-based</SelectItem>
                    <SelectItem value="Event-based">Event-based</SelectItem>
                    <SelectItem value="Condition-based">Condition-based</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button type="submit" onClick={addAutomation}>
                Add Automation
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent className={styles.cardContentAuto}>
        <div className="space-y-4">
          {automations.length === 0 ? (
            <p className="text-sm text-muted-foreground">No automations set up yet</p>
          ) : (
            automations.map((automation) => {
              const Icon = automationIcons[automation.icon] || Clock
              return (
                <div key={automation.id} className={styles.automationItemAuto}>
                  <div className={styles.detailsWrapperAuto}>
                    <div className={`${styles.iconWrapperAuto} ${automation.active ? styles.activeIconAuto : styles.inactiveIconAuto}`}>
                      <Icon className={styles.iconAuto} />
                    </div>
                    <div>
                      <p className={styles.detailsTextAuto}>{automation.name}</p>
                      <p className={styles.scheduleTextAuto}>{automation.schedule}</p>
                    </div>
                  </div>
                  <div className={styles.badgeWrapperAuto}>
                    <Badge variant="outline">{automation.type}</Badge>
                    <Switch checked={automation.active} onCheckedChange={() => toggleAutomation(automation.id)} />
                  </div>
                </div>
              )
            })
          )}
        </div>
      </CardContent>
    </Card>
  )
}
