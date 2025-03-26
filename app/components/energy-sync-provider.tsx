'use client';

import React, { ReactNode, useEffect } from 'react';
import useEnergySync from '@/app/hooks/useEnergySync';

interface EnergySyncProviderProps {
  children: ReactNode;
}

/**
 * Client component that initializes the energy consumption synchronization
 * across the application
 */
export default function EnergySyncProvider({ children }: EnergySyncProviderProps) {
  // Initialize the energy sync hook
  useEnergySync();
  
  return <>{children}</>;
} 