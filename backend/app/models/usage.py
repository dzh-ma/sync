"""
Models for device usage tracking.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field, field_validator

class CreateUsage(BaseModel):
    """
    Model for creating new device usage records.

    Attributes:
        device_id (str): ID of the device being monitored.
        metrics (Dict[str, Any]): Usage metrics specific to device type.
        timestamp (Optional[datetime]): When the usage was recorded (defaults to now).
        duration (Optional[int]): Duration of usage in seconds.
        energy_consumed (Optional[float]): Energy used in kWh.
        status (Optional[str]): Device status during measurement.
    """
    device_id: str
    metrics: Dict[str, Any]
    timestamp: Optional[datetime] = None
    duration: Optional[int] = None
    energy_consumed: Optional[float] = None
    status: Optional[str] = None

    @field_validator("device_id")
    @classmethod
    def validate_device_id(cls, v: str) -> str:
        """
        Validate device_id format.

        Args:
            v (str): Device ID to be validated.

        Returns:
            str: Validated device ID.

        Raises:
            ValueError: Invalid device ID format.
        """
        if not v or not isinstance(v, str):
            raise ValueError("Device ID must be a valid string")

        return v

    @field_validator("energy_consumed")
    @classmethod
    def validate_energy_consumed(cls, v: Optional[float]) -> Optional[float]:
        """
        Validate energy consumption is positive if provided.

        Args:
            v (Optional[float]): Energy consumption to be validated.

        Returns:
            Optional[float]: Validated energy consumption data.

        Raises:
            ValueError: Negative energy consumption.
        """
        if v is not None and v < 0:
            raise ValueError("Energy consumption cannot be negative")

        return v

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        """
        Validate duration is positive if provided.

        Args:
            v (Optional[int]): Energy consumption duration to be validated.

        Returns:
            Optional[int]: Validated energy duration data.

        Raises:
            ValueError: Negative duration.
        """
        if v is not None and v < 0:
            raise ValueError("Duration cannot be negative")

        return v


class UsageDB(BaseModel):
    """
    Internal model representing device usage data in the database.

    Attributes:
        id (str): Unique usage record identifier.
        device_id (str): ID of the device being monitored.
        metrics (Dict[str, Any]): Usage metrics specific to device type.
        timestamp (datetime): When the usage was recorded.
        duration (Optional[int]): Duration of usage in seconds.
        energy_consumed (Optional[float]): Energy used in kWh.
        status (Optional[str]): Device status during measurement.
        created (datetime): When this record was created.
        updated (Optional[datetime]): When this record was last updated.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    metrics: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration: Optional[int] = None
    energy_consumed: Optional[float] = None
    status: Optional[str] = None
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UsageResponse(BaseModel):
    """
    Model for usage data returned in API responses.

    Attributes:
        id (str): Unique usage record identifier.
        device_id (str): ID of the device being monitored.
        metrics (Dict[str, Any]): Usage metrics specific to device type.
        timestamp (datetime): When the usage was recorded.
        duration (Optional[int]): Duration of usage in seconds.
        energy_consumed (Optional[float]): Energy used in kWh.
        status (Optional[str]): Device status during measurement.
    """
    id: str
    device_id: str
    metrics: Dict[str, Any]
    timestamp: datetime
    duration: Optional[int] = None
    energy_consumed: Optional[float] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UsageUpdate(BaseModel):
    """
    Model for updating usage information.

    Attributes:
        metrics (Optional[Dict[str, Any]]): Updated metrics.
        duration (Optional[int]): Updated duration in seconds.
        energy_consumed (Optional[float]): Updated energy consumption in kWh.
        status (Optional[str]): Updated device status.
    """
    metrics: Optional[Dict[str, Any]] = None
    duration: Optional[int] = None
    energy_consumed: Optional[float] = None
    status: Optional[str] = None

    @field_validator("energy_consumed")
    @classmethod
    def validate_energy_consumed(cls, v: Optional[float]) -> Optional[float]:
        """
        Validate energy consumption is positive if provided.

        Args:
            v Optional[float]: Energy consumption metric to be validated.

        Returns:
            Optional[float]: Validated energy consumption data.

        Returns:
            ValueError: Negative energy consumption.
        """
        if v is not None and v < 0:
            raise ValueError("Energy consumption cannot be negative")

        return v

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v: Optional[int]) -> Optional[int]:
        """
        Validate duration is positive if provided.

        Args:
            v Optional[float]: Energy consumption duration to be validated.

        Returns:
            Optional[float]: Validated energy duration data.

        Returns:
            ValueError: Negative duration.
        """
        if v is not None and v < 0:
            raise ValueError("Duration cannot be negative")

        return v


class UsageAggregateResponse(BaseModel):
    """
    Model for aggregated usage statistics returned in API responses.

    Attributes:
        device_id (str): ID of the device being monitored.
        start_date (datetime): Start of the aggregation period.
        end_date (datetime): End of the aggregation period.
        total_duration (int): Total usage duration in seconds.
        total_energy (float): Total energy consumed in kWh.
        average_metrics (Dict[str, float]): Average of numeric metrics.
        usage_count (int): Number of usage records in the period.
    """
    device_id: str
    start_date: datetime
    end_date: datetime
    total_duration: int = 0
    total_energy: float = 0
    average_metrics: Dict[str, float] = {}
    usage_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class UsageBulkCreate(BaseModel):
    """
    Model for bulk creation of usage records.

    Attributes:
        records (List[CreateUsage]): List of usage records to create.
    """
    records: List[CreateUsage]

    @field_validator("records")
    @classmethod
    def validate_records(cls, v: List[CreateUsage]) -> List[CreateUsage]:
        """
        Validate records list is not empty.

        Args:
            v (List[CreateUsage]): Records to be validated.

        Returns:
            List[CreateUsage]: Validated usage records.

        Raises:
            ValueError: Records list is empty.
        """
        if not v:
            raise ValueError("Records list cannot be empty")

        return v


class UsageTimeRange(BaseModel):
    """
    Model for specifying a time range for usage queries.

    Attributes:
        start_time (datetime): Start of the time range.
        end_time (datetime): End of the time range.
        device_id (Optional[str]): Optional device ID to filter by.
    """
    start_time: datetime
    end_time: datetime
    device_id: Optional[str] = None

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: datetime, info) -> datetime:
        """
        Validate end_time is after start_time.
        """
        if info.data.get("start_time") and v < info.data.get("start_time"):
            raise ValueError("End time must be after start time")

        return v
