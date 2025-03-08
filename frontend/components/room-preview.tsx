import Image from "next/image"

export function RoomPreview() {
  return (
    <div className="relative h-[200px] rounded-xl overflow-hidden mt-4">
      <Image
        src="https://hebbkx1anhila5yf.public.blob.vercel-storage.com/IMG_0697-MRkZkq9qJMNVm20BYSDpYOdkYHt3pF.jpeg"
        alt="Living Room"
        fill
        className="object-cover"
      />
      <div className="absolute bottom-2 left-2 bg-white/80 px-2 py-1 rounded text-sm">Living Room</div>
    </div>
  )
}

