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
    
    // Check if API key is the default (not configured)
    if (API_KEY === "your_api_key_here") {
      console.warn("OpenWeatherMap API key not configured. Using mock data.");
      return NextResponse.json(generateMockWeatherData(city, units), { status: 200 });
    }
    
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
    
    // Get the requested city and units from query params even in error case
    const searchParams = request.nextUrl.searchParams;
    const city = searchParams.get("city") || "Edinburgh";
    const units = searchParams.get("units") || "metric";
    
    // Return mock data in case of failure
    return NextResponse.json(
      generateMockWeatherData(city, units),
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
  
  // Generate a more realistic temperature based on city
  let baseTemp;
  const currentMonth = new Date().getMonth(); // 0-11
  const isNorthernHemisphere = !["Sydney", "Melbourne", "Auckland", "Buenos Aires", "Cape Town", "Rio de Janeiro"].includes(city);
  
  // Seasonal adjustment - opposite for southern hemisphere
  const isSummer = isNorthernHemisphere ? (currentMonth >= 5 && currentMonth <= 8) : (currentMonth <= 2 || currentMonth >= 11);
  const isWinter = isNorthernHemisphere ? (currentMonth <= 1 || currentMonth >= 10) : (currentMonth >= 5 && currentMonth <= 8);
  
  // Base temperature by city type
  if (["Dubai", "Abu Dhabi", "Doha", "Riyadh", "Cairo"].includes(city)) {
    // Hot desert cities
    baseTemp = isSummer ? 38 : (isWinter ? 24 : 30);
  } else if (["London", "Edinburgh", "Paris", "Berlin", "Amsterdam"].includes(city)) {
    // European temperate cities
    baseTemp = isSummer ? 25 : (isWinter ? 5 : 15);
  } else if (["Moscow", "Helsinki", "Oslo", "Stockholm"].includes(city)) {
    // Cold northern cities
    baseTemp = isSummer ? 22 : (isWinter ? -5 : 10);
  } else if (["Miami", "Singapore", "Bangkok", "Mumbai"].includes(city)) {
    // Hot tropical cities
    baseTemp = isSummer ? 33 : (isWinter ? 25 : 29);
  } else if (["New York", "Toronto", "Chicago", "Boston"].includes(city)) {
    // North American cities
    baseTemp = isSummer ? 28 : (isWinter ? -2 : 15);
  } else {
    // Default for other cities
    baseTemp = isSummer ? 26 : (isWinter ? 8 : 18);
  }
  
  // Add some randomness for realism (+/- 3 degrees)
  const randomVariation = Math.floor(Math.random() * 7) - 3;
  const tempInCelsius = baseTemp + randomVariation;
  
  // Convert to Fahrenheit if needed
  const temperature = isCelsius ? tempInCelsius : Math.round(tempInCelsius * 9/5 + 32);
  
  // Different conditions based on temperature
  let condition: "sunny" | "cloudy" | "rainy" | "windy";
  let description: string;
  
  if (tempInCelsius > 30) {
    condition = "sunny";
    description = "clear sky";
  } else if (tempInCelsius < 5) {
    condition = "cloudy";
    description = "overcast clouds";
  } else {
    // Random condition for moderate temperatures
    const conditions = ["sunny", "cloudy", "rainy", "windy"];
    const descriptions = ["clear sky", "scattered clouds", "light rain", "moderate breeze"];
    const randomIndex = Math.floor(Math.random() * 4);
    condition = conditions[randomIndex] as "sunny" | "cloudy" | "rainy" | "windy";
    description = descriptions[randomIndex];
  }
  
  return {
    city: city,
    temperature: temperature,
    condition: condition,
    description: description,
    humidity: Math.floor(Math.random() * 30) + 40, // 40-70%
    windSpeed: isCelsius ? Math.floor(Math.random() * 15) + 5 : Math.floor(Math.random() * 10) + 3, // km/h or mph
    icon: condition === "sunny" ? "01d" : condition === "cloudy" ? "03d" : condition === "rainy" ? "10d" : "50d",
    units: units,
    timestamp: new Date().toISOString(),
  };
} 