"use client"

import * as React from "react"
import * as ProgressPrimitive from "@radix-ui/react-progress"

import { cn } from "@/lib/utils"

interface ProgressProps extends React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root> {
  indicatorClassName?: string;
  variant?: "default" | "excellent" | "good" | "fair" | "poor";
}

const Progress = React.forwardRef<
  React.ElementRef<typeof ProgressPrimitive.Root>,
  ProgressProps
>(({ className, value, indicatorClassName, variant = "default", ...props }, ref) => {
  // Get variant-specific indicator class
  const getVariantClass = () => {
    switch (variant) {
      case "excellent":
        return "bg-green-500";
      case "good":
        return "bg-yellow-400";
      case "fair":
        return "bg-amber-500";
      case "poor":
        return "bg-red-500";
      default:
        return "bg-[#00B2FF]";
    }
  };

  return (
    <ProgressPrimitive.Root
      ref={ref}
      className={cn(
        "relative h-2 w-full overflow-hidden rounded-full bg-gray-100",
        className
      )}
      {...props}
    >
      <ProgressPrimitive.Indicator
        className={cn(
          "h-full w-full flex-1 transition-all", 
          getVariantClass(),
          indicatorClassName
        )}
        style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
      />
    </ProgressPrimitive.Root>
  );
})
Progress.displayName = ProgressPrimitive.Root.displayName

export { Progress }
