import { NextRequest, NextResponse } from "next/server"

// MongoDB URL
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000"

export async function POST(request: NextRequest) {
  try {
    // Extract parameters if any
    const data = await request.json().catch(() => ({}));
    const userId = data.userId;
    const householdId = data.householdId;
    
    console.log(`Triggering statistics collection for userId=${userId}, householdId=${householdId}`);
    
    // Build URL with parameters
    let collectUrl = `${BACKEND_URL}/api/statistics/collect`;
    
    // If we have parameters, add them as query params
    const queryParams = [];
    if (userId) queryParams.push(`user_id=${encodeURIComponent(userId)}`);
    if (householdId) queryParams.push(`household_id=${encodeURIComponent(householdId)}`);
    
    if (queryParams.length > 0) {
      collectUrl += '?' + queryParams.join('&');
    }
    
    // Call backend to trigger statistics collection
    const response = await fetch(collectUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Failed to trigger statistics collection: ${response.status} ${response.statusText}`);
      console.error(`Error details: ${errorText}`);
      
      return NextResponse.json(
        { error: "Failed to trigger statistics collection" },
        { status: response.status }
      );
    }
    
    const result = await response.json();
    
    return NextResponse.json({
      message: "Statistics collection triggered successfully",
      details: result
    });
  } catch (error: any) {
    console.error("Error in statistics collection API:", error.message, error.stack);
    
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
} 