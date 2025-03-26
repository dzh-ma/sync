'use client';

import React, { ReactNode } from 'react';
import EnergySyncProvider from './energy-sync-provider';

interface ClientEnergySyncWrapperProps {
  children: ReactNode;
}

/**
 * Client component wrapper that safely uses client-side functionality
 * This is used to avoid the "ssr: false is not allowed in Server Components" error
 */
export default function ClientEnergySyncWrapper({ children }: ClientEnergySyncWrapperProps) {
  return (
    <EnergySyncProvider>
      {children}
    </EnergySyncProvider>
  );
} 