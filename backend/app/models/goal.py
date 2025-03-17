"""
Models for energy goal validation and storage.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, field_validator


class GoalType(str, Enum):
    """
    Enumeration of supported goal types.
    """
    ENERGY_SAVING = "energy_saving"
    CONSUMPTION_LIMIT = "consumption_limit"
    USAGE_REDUCTION = "usage_reduction"
    PEAK_AVOIDANCE = "peak_avoidance"
    RENEWABLE_USAGE = "renewable_usage"


class GoalStatus(str, Enum):
    """
    Enumeration of goal statuses.
    """
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class GoalTimeframe(str, Enum):
    """
    Enumeration of goal timeframes.
    """
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class CreateEnergyGoal(BaseModel):
    """
    Model for energy goal creation input.

    Attributes:
        user_id (str): ID of the user who owns the goal.
        title (str): Title of the goal.
        description (str): Detailed description of the goal.
        type (GoalType): Type of energy goal.
        target_value (float): Target value for the goal (e.g., kWh to save).
        timeframe (GoalTimeframe): Timeframe for the goal.
        start_date (datetime): When the goal starts.
        end_date (Optional[datetime]): When the goal ends (required for CUSTOM timeframe).
        related_devices (Optional[List[str]]): List of device IDs this goal applies to.
    """
    user_id: str
    title: str
    description: str
    type: GoalType
    target_value: float
    timeframe: GoalTimeframe
    start_date: datetime
    end_date: Optional[datetime] = None
    related_devices: Optional[List[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, t: str) -> str:
        """
        Validate the goal title.

        Arguments:
            t (str): Title to be validated.

        Returns:
            str: Validated title.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if len(t) < 3:
            raise ValueError("Title must be at least 3 characters long.")
        if len(t) > 100:
            raise ValueError("Title must be less than 100 characters long.")
        return t

    @field_validator("description")
    @classmethod
    def validate_description(cls, d: str) -> str:
        """
        Validate the goal description.

        Arguments:
            d (str): Description to be validated.

        Returns:
            str: Validated description.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if len(d) < 10:
            raise ValueError("Description must be at least 10 characters long.")
        if len(d) > 500:
            raise ValueError("Description must be less than 500 characters long.")
        return d

    @field_validator("target_value")
    @classmethod
    def validate_target_value(cls, v: float) -> float:
        """
        Validate the target value.

        Arguments:
            v (float): Target value to be validated.

        Returns:
            float: Validated target value.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if v <= 0:
            raise ValueError("Target value must be greater than 0.")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, end: Optional[datetime], values: dict) -> Optional[datetime]:
        """
        Validate the end date based on timeframe and start date.

        Arguments:
            end (Optional[datetime]): End date to be validated.
            values (dict): Previously validated values.

        Returns:
            Optional[datetime]: Validated end date.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        timeframe = values.data.get("timeframe")
        start_date = values.data.get("start_date")

        if timeframe == GoalTimeframe.CUSTOM and end is None:
            raise ValueError("End date is required for custom timeframe.")

        if end is not None and start_date is not None and end <= start_date:
            raise ValueError("End date must be after start date.")

        return end


class EnergyGoalDB(BaseModel):
    """
    Internal model representing energy goal data in the database.

    Attributes:
        id (str): Unique goal identifier.
        user_id (str): ID of the user who owns the goal.
        title (str): Title of the goal.
        description (str): Detailed description of the goal.
        type (GoalType): Type of energy goal.
        target_value (float): Target value for the goal (e.g., kWh to save).
        current_value (float): Current progress value.
        progress_percentage (float): Percentage of goal completion.
        timeframe (GoalTimeframe): Timeframe for the goal.
        start_date (datetime): When the goal starts.
        end_date (Optional[datetime]): When the goal ends.
        status (GoalStatus): Current status of the goal.
        related_devices (List[str]): List of device IDs this goal applies to.
        created (datetime): When the goal was created.
        updated (Optional[datetime]): When the goal was last updated.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    type: GoalType
    target_value: float
    current_value: float = 0.0
    progress_percentage: float = 0.0
    timeframe: GoalTimeframe
    start_date: datetime
    end_date: Optional[datetime] = None
    status: GoalStatus = GoalStatus.ACTIVE
    related_devices: List[str] = Field(default_factory=list)
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EnergyGoalResponse(BaseModel):
    """
    Model for energy goal data returned in API responses.

    Attributes:
        id (str): Unique goal identifier.
        user_id (str): ID of the user who owns the goal.
        title (str): Title of the goal.
        description (str): Detailed description of the goal.
        type (GoalType): Type of energy goal.
        target_value (float): Target value for the goal.
        current_value (float): Current progress value.
        progress_percentage (float): Percentage of goal completion.
        timeframe (GoalTimeframe): Timeframe for the goal.
        start_date (datetime): When the goal starts.
        end_date (Optional[datetime]): When the goal ends.
        status (GoalStatus): Current status of the goal.
        related_devices (List[str]): List of device IDs this goal applies to.
        created (datetime): When the goal was created.
    """
    id: str
    user_id: str
    title: str
    description: str
    type: str
    target_value: float
    current_value: float
    progress_percentage: float
    timeframe: str
    start_date: datetime
    end_date: Optional[datetime] = None
    status: str
    related_devices: List[str]
    created: datetime

    model_config = ConfigDict(from_attributes=True)


class EnergyGoalUpdate(BaseModel):
    """
    Model for updating energy goal information.

    Attributes:
        title (Optional[str]): Updated title of the goal.
        description (Optional[str]): Updated description of the goal.
        target_value (Optional[float]): Updated target value.
        current_value (Optional[float]): Updated current value.
        status (Optional[GoalStatus]): Updated goal status.
        end_date (Optional[datetime]): Updated end date.
        related_devices (Optional[List[str]]): Updated list of related devices.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    target_value: Optional[float] = None
    current_value: Optional[float] = None
    status: Optional[GoalStatus] = None
    end_date: Optional[datetime] = None
    related_devices: Optional[List[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, t: Optional[str]) -> Optional[str]:
        """
        Validate the goal title.

        Arguments:
            t (Optional[str]): Title to be validated.

        Returns:
            Optional[str]: Validated title.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if isinstance(t, str):
            if len(t) < 3:
                raise ValueError("Title must be at least 3 characters long.")
            if len(t) > 100:
                raise ValueError("Title must be less than 100 characters long.")
        return t

    @field_validator("description")
    @classmethod
    def validate_description(cls, d: Optional[str]) -> Optional[str]:
        """
        Validate the goal description.

        Arguments:
            d (Optional[str]): Description to be validated.

        Returns:
            Optional[str]: Validated description.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if isinstance(d, str):
            if len(d) < 10:
                raise ValueError("Description must be at least 10 characters long.")
            if len(d) > 500:
                raise ValueError("Description must be less than 500 characters long.")
        return d

    @field_validator("target_value")
    @classmethod
    def validate_target_value(cls, v: Optional[float]) -> Optional[float]:
        """
        Validate the target value.

        Arguments:
            v (Optional[float]): Target value to be validated.

        Returns:
            Optional[float]: Validated target value.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if v is not None and v <= 0:
            raise ValueError("Target value must be greater than 0.")
        return v

    @field_validator("current_value")
    @classmethod
    def validate_current_value(cls, v: Optional[float]) -> Optional[float]:
        """
        Validate the current value.

        Arguments:
            v (Optional[float]): Current value to be validated.

        Returns:
            Optional[float]: Validated current value.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if v is not None and v < 0:
            raise ValueError("Current value cannot be negative.")
        return v


class EnergyGoalProgressUpdate(BaseModel):
    """
    Model specifically for updating goal progress.

    Attributes:
        current_value (float): New current value for the goal.
    """
    current_value: float

    @field_validator("current_value")
    @classmethod
    def validate_current_value(cls, v: float) -> float:
        """
        Validate the current value.

        Arguments:
            v (float): Current value to be validated.

        Returns:
            float: Validated current value.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if v < 0:
            raise ValueError("Current value cannot be negative.")
        return v
