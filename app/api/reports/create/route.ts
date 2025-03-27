import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = "http://127.0.0.1:8000";

export async function POST(request: NextRequest) {
  try {
    // Get the user_id from the query parameters
    const url = new URL(request.url);
    const userId = url.searchParams.get('user_id');
    
    if (!userId) {
      return NextResponse.json(
        { error: "Missing user_id parameter" },
        { status: 400 }
      );
    }
    
    // Get the request body
    const requestBody = await request.json();
    
    // Forward the request to the backend
    const response = await fetch(`${BACKEND_URL}/api/reports/create?user_id=${encodeURIComponent(userId)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });
    
    // If the backend returns an error, pass it through
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Backend error: ${response.status} ${response.statusText}`);
      console.error("Error details:", errorText);
      
      return NextResponse.json(
        { error: `Backend error: ${response.status} ${response.statusText}`, details: errorText },
        { status: response.status }
      );
    }
    
    // Return the backend response
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error in reports/create API route:", error);
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
