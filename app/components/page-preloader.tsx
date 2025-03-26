"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

// List of all important routes in the app
const ALL_ROUTES = [
  "/dashboard",
  "/profile",
  "/settings",
  "/add-room",
  "/rooms",
  "/devices",
  "/statistics",
  "/suggestions",
  "/automations"
];

interface PagePreloaderProps {
  onProgress?: (progress: number) => void;
}

/**
 * Component that preloads all pages during initial app startup
 * to avoid the compile delay when visiting each page for the first time
 */
export function PagePreloader({ onProgress }: PagePreloaderProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Check if we've already done the preloading
    const hasPreloaded = localStorage.getItem('pagesPreloaded');
    if (hasPreloaded === 'true') {
      setIsLoading(false);
      if (onProgress) onProgress(100);
      return;
    }

    // Start preloading after a short delay to not block initial render
    const timer = setTimeout(() => {
      console.log("Starting to preload all pages...");
      
      let completed = 0;
      const totalPages = ALL_ROUTES.length;
      
      // Queue each route for preloading
      ALL_ROUTES.forEach((route, index) => {
        setTimeout(() => {
          console.log(`Preloading route: ${route}`);
          
          // Use the prefetch method if available
          // @ts-ignore - prefetch is not in the types but exists in the router
          if (router.prefetch) {
            // @ts-ignore
            router.prefetch(route);
          }
          
          // Use a hidden iframe as a fallback method to force page compilation
          const iframe = document.createElement('iframe');
          iframe.style.width = '0';
          iframe.style.height = '0';
          iframe.style.position = 'absolute';
          iframe.style.visibility = 'hidden';
          iframe.src = route;
          
          // Handle completion
          iframe.onload = () => {
            completed++;
            const newProgress = Math.round((completed / totalPages) * 100);
            setProgress(newProgress);
            if (onProgress) onProgress(newProgress);
            
            // Remove the iframe once loaded
            setTimeout(() => {
              document.body.removeChild(iframe);
              
              // If all pages are preloaded, mark as complete
              if (completed === totalPages) {
                console.log("All pages preloaded successfully!");
                localStorage.setItem('pagesPreloaded', 'true');
                setIsLoading(false);
              }
            }, 500);
          };
          
          document.body.appendChild(iframe);
        }, index * 500); // Stagger loading with 500ms intervals
      });
    }, 3000); // Wait 3 seconds before starting preload
    
    return () => clearTimeout(timer);
  }, [router, onProgress]);

  return null;
} 