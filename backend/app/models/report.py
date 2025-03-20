"""
Models for report generation and storage.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReportFormat(str, Enum):
    """
    Enumeration of supported report formats.
    """
    PDF = "pdf"
    CSV = "csv"


class ReportStatus(str, Enum):
    """
    Enumeration of report generation statuses.
    """
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class CreateReportRequest(BaseModel):
    """
    Model for report generation request.

    Attributes:
        user_id (str): ID of the user requesting the report.
        title (Optional[str]): Optional title for the report.
        format (ReportFormat): Desired report format.
        start_date (Optional[str]): Optional start date in YYYY-MM-DD format.
        end_date (Optional[str]): Optional end date in YYYY-MM-DD format.
        device_ids (Optional[List[str]]): Optional list of device IDs to include.
        report_type (Optional[str]): Type of report (e.g., "energy", "usage", "anomaly").
    """
    user_id: str
    title: Optional[str] = None
    format: ReportFormat = ReportFormat.PDF
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    device_ids: Optional[List[str]] = None
    report_type: str = "energy"

    @field_validator("title")
    @classmethod
    def validate_title(cls, title: Optional[str]) -> Optional[str]:
        """Validate report title."""
        if title is not None:
            if len(title) < 3:
                raise ValueError("Title must be at least 3 characters long")
            if len(title) > 100:
                raise ValueError("Title must be less than 100 characters long")
        return title

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_format(cls, date: Optional[str]) -> Optional[str]:
        """Validate date format."""
        if date is not None:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date must be in YYYY-MM-DD format")
        return date


class ReportDB(BaseModel):
    """
    Internal model representing report data in the database.

    Attributes:
        id (str): Unique report identifier.
        user_id (str): ID of the user who requested the report.
        title (str): Report title.
        format (ReportFormat): Report format.
        file_path (Optional[str]): Path to the generated report file.
        status (ReportStatus): Current status of report generation.
        start_date (Optional[str]): Start date for report data.
        end_date (Optional[str]): End date for report data.
        device_ids (List[str]): Device IDs included in the report.
        created (datetime): When the report was requested.
        completed (Optional[datetime]): When the report generation finished.
        error_message (Optional[str]): Error message if generation failed.
        metadata (Dict[str, Any]): Additional report metadata.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    format: ReportFormat
    file_path: Optional[str] = None
    status: ReportStatus = ReportStatus.PENDING
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    device_ids: List[str] = Field(default_factory=list)
    report_type: str = "energy"
    created: datetime = Field(default_factory=datetime.utcnow)
    completed: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class ReportResponse(BaseModel):
    """
    Model for report data returned in API responses.

    Attributes:
        id (str): Unique report identifier.
        user_id (str): ID of the user who requested the report.
        title (str): Report title.
        format (ReportFormat): Report format.
        status (ReportStatus): Current status of report generation.
        created (datetime): When the report was requested.
        completed (Optional[datetime]): When the report generation finished.
        download_url (Optional[str]): URL to download the report file.
    """
    id: str
    user_id: str
    title: str
    format: str
    status: str
    report_type: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    device_ids: List[str] = []
    created: datetime
    completed: Optional[datetime] = None
    download_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
