"use client"

import { Card } from "@/components/ui/card"
import styles from './AirConditionerControl.module.css'

export function AirConditionerControl() {
  return (
    <Card className={styles.cardAir}>
      <h3 className={styles.cardTitleAir}>Air Conditioner</h3>
      {/* Add air conditioner control UI here */}
    </Card>
  )
}
