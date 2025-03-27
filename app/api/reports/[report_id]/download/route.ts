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
    const response = await fetch(`${BACKEND_URL}/api/reports/${encodeURIComponent(reportId)}/download`, {
      method: 'GET',
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
    
    // Read the PDF file content
    const pdfBuffer = await response.arrayBuffer();
    
    // Get the filename from the Content-Disposition header if available
    let filename = `report-${reportId}.pdf`;
    const contentDisposition = response.headers.get('Content-Disposition');
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="?([^"]+)"?/);
      if (match && match[1]) {
        filename = match[1];
      }
    }
    
    // Get the content type
    const contentType = response.headers.get('Content-Type') || 'application/pdf';
    
    // Return the file as a response
    return new NextResponse(pdfBuffer, {
      headers: {
        'Content-Type': contentType,
        'Content-Disposition': `attachment; filename="${filename}"`,
      },
    });
  } catch (error) {
    console.error(`Error in reports/[report_id]/download API route:`, error);
    return NextResponse.json(
      { error: "Internal server error", details: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}
