import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = "http://127.0.0.1:8000";

export async function GET(
  request: NextRequest,
  { params }: { params: { report_id: string } }
) {
  try {
    const reportId = params.report_id;
    
    if (!reportId) {
      return NextResponse.json(
        { error: "Missing report_id parameter" },
        { status: 400 }
      );
    }
    
    // Forward the request to the backend
    const response = await fetch(`${BACKEND_URL}/api/reports/${encodeURIComponent(reportId)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
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
    console.error(`Error in reports/[report_id] API route:`, error);
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
