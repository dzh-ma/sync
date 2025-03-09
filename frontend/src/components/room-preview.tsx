"use client"

import React from "react"
import { Card, CardHeader, CardTitle, CardContent } from "../../components/ui/card"
import Image from "next/image"

interface RoomPreviewProps {
  room: string
}

export function RoomPreview({ room }: RoomPreviewProps) {
  return (
    <Card className="mt-4">
      <CardHeader>
        <CardTitle>{room} Preview</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative h-48 rounded-md overflow-hidden">
          <Image
            src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/IMG_0697-MRkZkq9qJMNVm20BYSDpYOdkYHt3pF.jpeg"
            alt={`${room} Preview`}
            layout="fill"
            objectFit="cover"
          />
        </div>
      </CardContent>
    </Card>
  )
}

