"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

interface PrefetchProps {
  routes: string[];
}

/**
 * A component that prefetches routes to improve navigation performance
 * 
 * @param routes An array of routes to prefetch
 */
export function Prefetch({ routes }: PrefetchProps) {
  const router = useRouter();

  useEffect(() => {
    // This effect runs only once when the app starts
    if (typeof window !== 'undefined') {
      // Don't prefetch routes immediately to avoid slowing down initial page load
      const prefetchTimer = setTimeout(() => {
        console.log("Prefetching routes:", routes);
        
        // Prefetch each route with a slight delay to not overwhelm the system
        routes.forEach((route, index) => {
          setTimeout(() => {
            // @ts-ignore - prefetch is not in the types but exists in the router
            if (router.prefetch) {
              // @ts-ignore
              router.prefetch(route);
            }
          }, index * 300); // Add 300ms delay between each prefetch
        });
      }, 2000); // Wait 2 seconds after component mounts before starting prefetching
      
      return () => clearTimeout(prefetchTimer);
    }
  }, [routes, router]);

  // This component doesn't render anything
  return null;
} 