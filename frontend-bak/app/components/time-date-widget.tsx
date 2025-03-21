"use client";

import { useState, useEffect } from "react";
import { Calendar, Clock } from "lucide-react";

export function TimeDateWidget() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => {
      clearInterval(timer);
    };
  }, []);

  // Format time as HH:MM:SS
  const formattedTime = currentTime.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  });

  // Format date as Day, Month DD, YYYY
  const formattedDate = currentTime.toLocaleDateString([], {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  return (
    <div className="flex flex-col items-center justify-center h-full py-2">
      <div className="flex items-center mb-2">
        <Clock className="w-5 h-5 mr-2 text-blue-500" />
        <div className="text-2xl font-bold">{formattedTime}</div>
      </div>
      <div className="flex items-center">
        <Calendar className="w-4 h-4 mr-2 text-blue-500" />
        <div className="text-sm text-gray-600">{formattedDate}</div>
      </div>
    </div>
  );
}
