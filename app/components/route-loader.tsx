"use client";

import { useEffect, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";

/**
 * A minimal route loading indicator component that shows a progress bar at the top of
 * the screen during navigation.
 */
export function RouteLoader() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    
    // Set a timeout to stop showing the loader 
    // This simulates a loading state for very fast transitions
    const timeout = setTimeout(() => {
      setLoading(false);
    }, 500);
    
    return () => clearTimeout(timeout);
  }, [pathname, searchParams]);

  if (!loading) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 h-1 bg-[#FF9500] overflow-hidden">
      <div 
        className="h-full bg-[#00B2FF] transition-all duration-300 ease-in-out"
        style={{ 
          width: '40%',
          animation: 'indeterminate 1.5s infinite ease-in-out',
        }}
      />
      <style jsx>{`
        @keyframes indeterminate {
          0% {
            left: -40%;
          }
          100% {
            left: 100%;
          }
        }
        div div {
          position: absolute;
          will-change: transform;
        }
      `}</style>
    </div>
  );
} 