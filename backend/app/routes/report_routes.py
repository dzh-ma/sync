from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
import pandas as pd
from reportlab.pdfgen import canvas
import os
import datetime
from app.db.database import get_energy_data

router = APIRouter()

REPORTS_DIR = "generated_reports"
os.makedirs(REPORTS_DIR, exist_ok = True)

@router.post("/report")
async def generate_report(
        format: str = Query("csv", enum = ["csv", "pdf"]),
        start_date: str = Query(None, description = "Start date (YYYY-MM-DD)"),
        end_date: str = Query(None, description = "End date (YYYY-MM-DD)")
):
    """
    Generate an energy consumption report in CSV or PDF format,
    optionally filtered by date range.
    """
    try:
        energy_data = get_energy_data(start_date, end_date)
    except ValueError as exc:
        raise HTTPException(status_code = 400, detail = str(exc))

    if not energy_data:
        raise HTTPException(status_code = 404, detail = "No energy data available for the selected range.")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{REPORTS_DIR}/energy_report_{timestamp}.{format}"

    if format == "csv":
        df = pd.DataFrame(energy_data)
        df.to_csv(filename, index = False)
    elif format == "pdf":
        c = canvas.Canvas(filename)
        c.drawString(100, 750, "Energy Consumption Report")

        y_position = 730

        # Limit entries for readability
        for entry in energy_data[:10]:
            c.drawString(100, y_position, str(entry))
            y_position -= 20

        c.save()

    return FileResponse(
        path  = os.path.abspath(filename),
        filename = os.path.basename(filename),
        media_type = "application/octet-stream"
    )
