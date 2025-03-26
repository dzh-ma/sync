'use client';

import React, { ReactNode } from 'react';
import * as TooltipPrimitive from '@radix-ui/react-tooltip';
import { cn } from '@/lib/utils';

interface NavigationTooltipProps {
  label: string;
  description: string;
  children: ReactNode;
}

/**
 * A custom tooltip component specifically for navigation items
 * This ensures tooltips are properly positioned and appear above other content
 */
export function NavigationTooltip({ label, description, children }: NavigationTooltipProps) {
  return (
    <TooltipPrimitive.Provider delayDuration={100}>
      <TooltipPrimitive.Root>
        <TooltipPrimitive.Trigger asChild>
          {children}
        </TooltipPrimitive.Trigger>
        <TooltipPrimitive.Portal>
          <TooltipPrimitive.Content
            sideOffset={12}
            side="right"
            align="center"
            className={cn(
              "z-[9999] overflow-hidden rounded-md border-0 bg-white px-3 py-2 shadow-lg navigation-tooltip",
              "data-[state=delayed-open]:data-[side=right]:animate-in data-[state=delayed-open]:data-[side=right]:fade-in-0",
              "data-[state=delayed-open]:data-[side=right]:slide-in-from-left-2",
            )}
            collisionPadding={20}
          >
            <div className="font-semibold text-gray-800">{label}</div>
            <div className="text-xs text-gray-500 mt-1">{description}</div>
            <TooltipPrimitive.Arrow className="fill-white" />
          </TooltipPrimitive.Content>
        </TooltipPrimitive.Portal>
      </TooltipPrimitive.Root>
    </TooltipPrimitive.Provider>
  );
} 