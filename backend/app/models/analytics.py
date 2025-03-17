"""
Models for analytics validation and storage.
"""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateAnalytics(BaseModel):
    """
    Model for analytics data input.

    Attributes:
        user_id (str): ID of the user the analytics belongs to.
        device_id (str): ID of the device generating the analytics.
        data_type (str): Type of analytics data (energy, usage, temperature, etc.).
        metrics (Dict[str, Any]): The actual metrics being stored.
        tags (List[str]): Optional tags for categorizing analytics data.
    """
    user_id: str
    device_id: str
    data_type: str
    metrics: Dict[str, Any]
    tags: Optional[List[str]] = []

    @field_validator("user_id", "device_id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """
        Validate ID fields.

        Arguments:
            v (str): ID to be validated.

        Returns:
            str: Validated ID.

        Raises:
            ValueError: If ID is empty or doesn't match UUID format.
        """
        if not v:
            raise ValueError("ID cannot be empty.")
        
        # Try to parse as UUID to ensure valid format
        try:
            uuid.UUID(v)
        except ValueError as exc:
            raise ValueError("ID must be a valid UUID format.") from exc
            
        return v
    
    @field_validator("data_type")
    @classmethod
    def validate_data_type(cls, v: str) -> str:
        """
        Validate data_type field.

        Arguments:
            v (str): data_type to be validated.

        Returns:
            str: Validated data_type.

        Raises:
            ValueError: If data_type is empty or invalid.
        """
        valid_types = ["energy", "usage", "temperature", "humidity", "motion", "light", "other"]
        if not v:
            raise ValueError("Data type cannot be empty.")
        
        if v.lower() not in valid_types:
            raise ValueError(f"Data type must be one of: {', '.join(valid_types)}")
            
        return v.lower()


# What gets stored in MongoDB
class AnalyticsDB(BaseModel):
    """
    Internal model representing analytics data in the database.

    Attributes:
        id (str): Unique analytics identifier.
        user_id (str): ID of the user the analytics belongs to.
        device_id (str): ID of the device generating the analytics.
        data_type (str): Type of analytics data.
        metrics (Dict[str, Any]): The actual metrics being stored.
        tags (List[str]): Tags for categorizing analytics data.
        timestamp (datetime): When the analytics data was recorded.
        updated (Optional[datetime]): When the analytics data was last updated.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    device_id: str
    data_type: str
    metrics: Dict[str, Any]
    tags: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# What gets returned in API responses
class AnalyticsResponse(BaseModel):
    """
    Model for analytics data returned in API responses.

    Attributes:
        id (str): Unique analytics identifier.
        user_id (str): ID of the user the analytics belongs to.
        device_id (str): ID of the device generating the analytics.
        data_type (str): Type of analytics data.
        metrics (Dict[str, Any]): The actual metrics being stored.
        tags (List[str]): Tags for categorizing analytics data.
        timestamp (datetime): When the analytics data was recorded.
    """
    id: str
    user_id: str
    device_id: str
    data_type: str
    metrics: Dict[str, Any]
    tags: List[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# For updating analytics information
class AnalyticsUpdate(BaseModel):
    """
    Model for updating analytics information.

    Attributes:
        metrics (Optional[Dict[str, Any]]): Updated metrics.
        tags (Optional[List[str]]): Updated tags for categorizing analytics data.
    """
    metrics: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """
        Validate tags.

        Arguments:
            v (Optional[List[str]]): Tags to be validated.

        Returns:
            Optional[List[str]]: Validated tags.

        Raises:
            ValueError: If tags contain empty strings.
        """
        if v is not None:
            if any(not tag.strip() for tag in v):
                raise ValueError("Tags cannot contain empty strings.")
            return [tag.strip() for tag in v]
        return v


# For querying analytics data with filters
class AnalyticsQuery(BaseModel):
    """
    Model for querying analytics data with filters.

    Attributes:
        user_id (Optional[str]): Filter by user ID.
        device_id (Optional[str]): Filter by device ID.
        data_type (Optional[str]): Filter by data type.
        start_time (Optional[datetime]): Filter by start timestamp.
        end_time (Optional[datetime]): Filter by end timestamp.
        tags (Optional[List[str]]): Filter by tags.
    """
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    data_type: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tags: Optional[List[str]] = None

    @field_validator("start_time", "end_time")
    @classmethod
    def validate_time_range(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """
        Validate that start_time comes before end_time if both are provided.
        
        Note: This validation only runs after all fields are populated, so it
        needs to be called separately after instantiation.
        """
        return v
    
    def validate_time_range_post_init(self):
        """
        Validate that start_time comes before end_time if both are provided.
        Call this after instantiating the model.
        """
        if self.start_time and self.end_time and self.start_time > self.end_time:
            raise ValueError("start_time must be before end_time")
