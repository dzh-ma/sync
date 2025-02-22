"""
This module provides API endpoints for generating energy consumption reports

It includes:
- An endpoint to generate reports in CSV or PDF format, optionally filtered by a data range
- Reports are stored in the `generated_reports` directory
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes  import letter
import os
import datetime
from app.db.database import get_energy_data
from app.core.security import role_required

router = APIRouter()

# Directory for storing generated reports
REPORTS_DIR = "generated_reports"
os.makedirs(REPORTS_DIR, exist_ok = True)

@router.post("/report", dependencies = [Depends(role_required("admin"))])
async def generate_report(
        format: str = Query("csv", enum = ["csv", "pdf"]),
        start_date: str = Query(None, description = "Start date (YYYY-MM-DD)"),
        end_date: str = Query(None, description = "End date (YYYY-MM-DD)")
):
    """
    Generate an energy consumption report in CSV or PDF format

    Args:
        format (str): The desired report format, either "csv" or "pdf"
        start_date (str, optional): The start date for filtering data (YYYY-MM-DD)
        end_date (str, optional): The end date for filtering data (YYYY-MM-DD)

    Returns:
        FileResponse: The generated report file

    Raises:
        HTTPException (400): If an invalid date format is provided
        HTTPException (404): If no energy data is available for the selected range
    """
    try:
        energy_data = get_energy_data(start_date, end_date)
    except ValueError as exc:
        raise HTTPException(status_code = 400, detail = str(exc)) from exc

    if not energy_data:
        raise HTTPException(status_code = 404, detail = "No energy data available for the selected range.")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{REPORTS_DIR}/energy_report_{timestamp}.{format}"

    if format == "csv":
        # Convert data to a DataFrame & format timestamps
        df = pd.DataFrame(energy_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")  # Format timestamp
        df.columns = ["Device ID", "Timestamp", "Energy Consumed (kWh)", "Location"]
        df.to_csv(filename, index = False)
    elif format == "pdf":
        # Create a PDF report with a structure table
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []

        # Prepare table data
        data = [["Device ID", "Timestamp", "Energy Cosumed (kWh)", "Location"]]
        for entry in energy_data:
            data.append([
                entry.get("device_id", "N/A"),
                entry.get("timestamp", "").strftime('%Y-%m-%d %H:%M:%S') if entry.get("timestamp") else "N/A",
                entry.get("energy_consumed", "N/A"),
                entry.get("location", "N/A")
            ])

        # Create & style table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey])
        ]))

        elements.append(table)
        doc.build(elements)

    return FileResponse(
        path  = os.path.abspath(filename),
        filename = os.path.basename(filename),
        media_type = "application/octet-stream"
    )
