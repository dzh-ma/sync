import { NextRequest, NextResponse } from "next/server";

// OpenWeatherMap API configuration
const API_KEY = process.env.OPENWEATHER_API_KEY || "your_api_key_here"; // Replace with your API key or set in environment
const BASE_URL = "https://api.openweathermap.org/data/2.5";

export async function GET(request: NextRequest) {
  try {
    // Get location from query parameters, default to Edinburgh
    const searchParams = request.nextUrl.searchParams;
    const city = searchParams.get("city") || "Edinburgh";
    const units = searchParams.get("units") || "metric"; // metric (Celsius), imperial (Fahrenheit)
    
    // Fetch weather data from OpenWeatherMap
    const response = await fetch(
      `${BASE_URL}/weather?q=${encodeURIComponent(city)}&units=${units}&appid=${API_KEY}`,
      { next: { revalidate: 3600 } } // Cache for 1 hour
    );
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Weather API error: ${response.status} ${response.statusText}`);
      console.error(`Error details: ${errorText}`);
      
      // Return mock data if the API fails
      return NextResponse.json(generateMockWeatherData(city, units), { status: 200 });
    }
    
    const data = await response.json();
    
    // Transform the API response into a simpler format
    const weatherData = {
      city: city,
      temperature: Math.round(data.main.temp),
      condition: mapWeatherCondition(data.weather[0].main),
      description: data.weather[0].description,
      humidity: data.main.humidity,
      windSpeed: Math.round(data.wind.speed),
      icon: data.weather[0].icon,
      units: units,
      timestamp: new Date().toISOString(),
    };
    
    return NextResponse.json(weatherData);
  } catch (error: any) {
    console.error("Error fetching weather data:", error.message);
    
    // Return mock data in case of failure
    return NextResponse.json(
      generateMockWeatherData("Edinburgh", "metric"),
      { status: 200 }
    );
  }
}

// Map OpenWeatherMap conditions to our simplified conditions
function mapWeatherCondition(condition: string): "sunny" | "cloudy" | "rainy" | "windy" {
  switch (condition.toLowerCase()) {
    case "clear":
      return "sunny";
    case "clouds":
      return "cloudy";
    case "rain":
    case "drizzle":
    case "thunderstorm":
      return "rainy";
    case "snow":
    case "mist":
    case "fog":
    case "haze":
    default:
      // For now, anything else is considered cloudy
      return "cloudy";
  }
}

// Generate mock weather data for fallback or testing
function generateMockWeatherData(city: string, units: string) {
  const isCelsius = units === "metric";
  return {
    city: city,
    temperature: isCelsius ? 18 : 65, // Default temperatures
    condition: "sunny" as const,
    description: "clear sky",
    humidity: 45,
    windSpeed: isCelsius ? 10 : 6, // km/h or mph
    icon: "01d",
    units: units,
    timestamp: new Date().toISOString(),
  };
} 