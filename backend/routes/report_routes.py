"""
This module provides API endpoints for generating energy consumption reports.
It includes enhanced reporting with visualizations, analytics, and personalized insights.
"""
import os
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import FileResponse

from ..core.security import role_required, get_current_user
from ..db.database import get_energy_data
from ..utils.report_utils import generate_enhanced_report

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"],
    responses={404: {"description": "Not found"}},
)

# Reports directory (will be created if it doesn't exist)
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

@router.post("/report", dependencies=[Depends(role_required("admin"))])
async def generate_report(
    format: str = Query("pdf", enum=["csv", "pdf"]),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user)
) -> FileResponse:
    """
    Generate an enhanced energy consumption report with visualizations and analytics
    
    Args:
        format (str): The desired report format, either "pdf" or "csv"
        start_date (str, optional): The start date for filtering data (YYYY-MM-DD)
        end_date (str, optional): The end date for filtering data (YYYY-MM-DD)
        current_user (dict): The current authenticated user
    
    Returns:
        FileResponse: The generated report file
    
    Raises:
        HTTPException (400): If an invalid date format is provided
        HTTPException (404): If no energy data is available for the selected range
        HTTPException (500): If report generation fails
    """
    try:
        # Get energy data with optional date filtering
        energy_data = get_energy_data(start_date, end_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    if not energy_data:
        raise HTTPException(
            status_code=404, 
            detail="No energy data available for the selected range."
        )
    
    # Create user data for personalization
    user_data = {
        "email": current_user.get("sub", ""),
        "role": current_user.get("role", "user")
    }
    
    # Generate the enhanced report
    try:
        report_path = generate_enhanced_report(
            energy_data=energy_data,
            format=format,
            user_data=user_data,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating report: {str(e)}"
        )
    
    # Return the generated file
    return FileResponse(
        path=os.path.abspath(report_path),
        filename=os.path.basename(report_path),
        media_type="application/octet-stream"
    )
