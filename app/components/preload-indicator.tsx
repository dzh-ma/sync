"use client";

import { useState, useEffect } from "react";
import { Progress } from "@/components/ui/progress";
import { PagePreloader } from "@/app/components/page-preloader";

export function PreloadIndicator() {
  const [progress, setProgress] = useState(0);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    // Hide the indicator when progress reaches 100%
    if (progress >= 100) {
      // Wait a moment before hiding to show the completed progress
      const timer = setTimeout(() => {
        setVisible(false);
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [progress]);

  // If we've already preloaded, don't show the indicator
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const hasPreloaded = localStorage.getItem('pagesPreloaded') === 'true';
      if (hasPreloaded) {
        setVisible(false);
      }
    }
  }, []);

  if (!visible) return null;

  return (
    <>
      <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center">
        <div className="bg-white p-6 rounded-lg shadow-xl w-[90%] max-w-md">
          <div className="flex items-center justify-center mb-4">
            <span className="text-2xl font-bold bg-[#00B2FF] text-white px-3 py-1 rounded-full mr-2">
              Sy<span className="text-[#FFB800]">nc</span>
            </span>
          </div>
          <h3 className="text-lg font-medium text-center mb-4">
            Optimizing App Performance
          </h3>
          <p className="text-sm text-gray-500 text-center mb-6">
            Loading all pages for instant navigation ({progress}%)
          </p>
          <Progress value={progress} className="h-2 mb-2" />
          <p className="text-xs text-gray-400 text-center mt-2">
            This will only happen once and will make navigation smoother.
          </p>
        </div>
      </div>
      <PagePreloader onProgress={setProgress} />
    </>
  );
} 