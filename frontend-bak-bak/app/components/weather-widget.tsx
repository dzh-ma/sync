"use client";

import { useState, useEffect } from "react";
import { Cloud, CloudRain, Sun, Wind, Snowflake, CloudLightning } from "lucide-react";

// In a real application, you would use a weather API like OpenWeatherMap
// This is a simplified mock implementation
interface WeatherData {
  temperature: number;
  condition: string;
  humidity: number;
  windSpeed: number;
  location: string;
}

export function WeatherWidget() {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching weather data
    const fetchWeather = async () => {
      setIsLoading(true);
      try {
        // Replace with actual API call in production
        // const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?q=YourCity&appid=YourAPIKey&units=metric`);
        // const data = await response.json();
        
        // Mock data for demonstration
        setTimeout(() => {
          const conditions = ["Sunny", "Cloudy", "Rainy", "Windy", "Snowy", "Thunderstorm"];
          const randomCondition = conditions[Math.floor(Math.random() * conditions.length)];
          
          const mockWeather: WeatherData = {
            temperature: Math.floor(Math.random() * 35) + 5, // 5-40°C
            condition: randomCondition,
            humidity: Math.floor(Math.random() * 60) + 40, // 40-100%
            windSpeed: Math.floor(Math.random() * 30) + 1, // 1-30 km/h
            location: "Your City" // Would be dynamically determined in production
          };
          
          setWeather(mockWeather);
          setIsLoading(false);
        }, 1000);
      } catch (error) {
        console.error("Error fetching weather data:", error);
        setIsLoading(false);
      }
    };

    fetchWeather();
    
    // Refresh weather data every 30 minutes
    const intervalId = setInterval(fetchWeather, 30 * 60 * 1000);
    
    return () => clearInterval(intervalId);
  }, []);

  const getWeatherIcon = (condition: string) => {
    switch (condition.toLowerCase()) {
      case "sunny":
        return <Sun className="w-12 h-12 text-yellow-500" />;
      case "cloudy":
        return <Cloud className="w-12 h-12 text-gray-400" />;
      case "rainy":
        return <CloudRain className="w-12 h-12 text-blue-400" />;
      case "windy":
        return <Wind className="w-12 h-12 text-gray-500" />;
      case "snowy":
        return <Snowflake className="w-12 h-12 text-blue-300" />;
      case "thunderstorm":
        return <CloudLightning className="w-12 h-12 text-purple-500" />;
      default:
        return <Cloud className="w-12 h-12 text-gray-400" />;
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-12 h-12 bg-gray-300 rounded-full mb-3"></div>
          <div className="h-4 w-20 bg-gray-300 rounded mb-2"></div>
          <div className="h-3 w-24 bg-gray-300 rounded"></div>
        </div>
      </div>
    );
  }

  if (!weather) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <p className="text-sm text-gray-500">Weather data unavailable</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center h-full">
      {getWeatherIcon(weather.condition)}
      <div className="mt-2 text-xl font-bold">{weather.temperature}°C</div>
      <div className="text-sm text-gray-600">{weather.condition}</div>
      <div className="flex justify-between w-full mt-3 text-xs text-gray-500">
        <div>Humidity: {weather.humidity}%</div>
        <div>Wind: {weather.windSpeed} km/h</div>
      </div>
      <div className="text-xs text-gray-500 mt-1">{weather.location}</div>
    </div>
  );
}
