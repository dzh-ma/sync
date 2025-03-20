"""
API routes for report generation and management.
"""
import os
import asyncio
import concurrent.futures
from functools import wraps
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Path, Query, status
from fastapi.responses import FileResponse
from typing import List, Optional

from app.models.report import (
    CreateReportRequest, 
    ReportResponse, 
    ReportDB,
    ReportStatus
)
from app.services.report_service import ReportService

# Create router
router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}},
)

# Create thread pool for running sync code
executor = concurrent.futures.ThreadPoolExecutor()

def run_in_executor(func):
    """
    Decorator to run synchronous functions in a thread pool executor.
    Makes them non-blocking for FastAPI's async framework.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(
            executor, lambda: func(*args, **kwargs)
        )
    return wrapper

@router.post("/", status_code=status.HTTP_202_ACCEPTED, response_model=ReportResponse)
async def create_report(
    request: CreateReportRequest,
    background_tasks: BackgroundTasks
):
    """
    Request generation of a new energy report.
    
    The report will be generated asynchronously in the background.
    """
    # Create a title if none provided
    if not request.title:
        timeframe = ""
        if request.start_date and request.end_date:
            timeframe = f" ({request.start_date} to {request.end_date})"
        request.title = f"Energy Report{timeframe}"
    
    # Create report record
    report_db = ReportDB(
        user_id=request.user_id,
        title=request.title,
        format=request.format,
        start_date=request.start_date,
        end_date=request.end_date,
        device_ids=request.device_ids or [],
        report_type=request.report_type
    )
    
    # Save to database - run in executor to make it non-blocking
    report_id = await run_in_executor(ReportService.create_report)(report_db)
    
    # Start background task to generate report - will run in thread pool
    @run_in_executor
    def generate_report_wrapper(report_id):
        return ReportService.generate_report(report_id)
    
    background_tasks.add_task(generate_report_wrapper, report_id)
    
    # Get the created report - run in executor to make it non-blocking
    report = await run_in_executor(ReportService.get_report)(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report"
        )
    
    # Create response with download URL
    response = ReportResponse(
        id=report["id"],
        user_id=report["user_id"],
        title=report["title"],
        format=report["format"],
        status=report["status"],
        report_type=report["report_type"],
        start_date=report.get("start_date"),
        end_date=report.get("end_date"),
        device_ids=report.get("device_ids", []),
        created=report["created"],
        completed=report.get("completed"),
        download_url=f"/api/v1/reports/{report['id']}/download" if report["status"] == ReportStatus.COMPLETED else None
    )
    
    return response


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str = Path(..., description="ID of the report to retrieve")
):
    """
    Get the status and details of a specific report.
    """
    report = await run_in_executor(ReportService.get_report)(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Create response
    response = ReportResponse(
        id=report["id"],
        user_id=report["user_id"],
        title=report["title"],
        format=report["format"],
        status=report["status"],
        report_type=report["report_type"],
        start_date=report.get("start_date"),
        end_date=report.get("end_date"),
        device_ids=report.get("device_ids", []),
        created=report["created"],
        completed=report.get("completed"),
        download_url=f"/api/v1/reports/{report['id']}/download" if report["status"] == ReportStatus.COMPLETED else None
    )
    
    return response


@router.get("/user/{user_id}", response_model=List[ReportResponse])
async def get_user_reports(
    user_id: str = Path(..., description="ID of the user"),
    limit: int = Query(10, description="Maximum number of reports to return"),
    offset: int = Query(0, description="Offset for pagination")
):
    """
    Get all reports for a specific user.
    """
    reports = await run_in_executor(ReportService.get_user_reports)(user_id)
    
    # Apply pagination
    paginated_reports = reports[offset:offset+limit]
    
    # Create response
    responses = []
    for report in paginated_reports:
        responses.append(
            ReportResponse(
                id=report["id"],
                user_id=report["user_id"],
                title=report["title"],
                format=report["format"],
                status=report["status"],
                report_type=report["report_type"],
                start_date=report.get("start_date"),
                end_date=report.get("end_date"),
                device_ids=report.get("device_ids", []),
                created=report["created"],
                completed=report.get("completed"),
                download_url=f"/api/v1/reports/{report['id']}/download" if report["status"] == ReportStatus.COMPLETED else None
            )
        )
    
    return responses


@router.get("/{report_id}/download")
async def download_report(
    report_id: str = Path(..., description="ID of the report to download")
):
    """
    Download a generated report file.
    """
    report = await run_in_executor(ReportService.get_report)(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report["status"] != ReportStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report is not ready for download. Current status: {report['status']}"
        )
    
    file_path = report.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    # Determine file type for content-type header
    media_type = "application/pdf" if report["format"].lower() == "pdf" else "text/csv"
    
    # Get filename from path
    filename = os.path.basename(file_path)
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: str = Path(..., description="ID of the report to delete")
):
    """
    Delete a report and its associated file.
    """
    report = await run_in_executor(ReportService.get_report)(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Delete the file if it exists
    file_path = report.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            # Log but don't fail if file deletion fails
            pass
    
    # Delete from database
    result = await run_in_executor(ReportService.delete_report)(report_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )
    
    return None
