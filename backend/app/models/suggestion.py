"""
Models for suggestion validation.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator

class SuggestionStatus(str, Enum):
    """
    Enum for suggestion status.
    """
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"

class SuggestionType(str, Enum):
    """
    Enum for suggestion types.
    """
    ENERGY_SAVING = "energy_saving"
    SECURITY = "security"
    COMFORT = "comfort"
    AUTOMATION = "automation"
    OTHER = "other"

class CreateSuggestion(BaseModel):
    """
    Model for suggestion creation input.

    Attributes:
        user_id (str): ID of the user who receives the suggestion.
        title (str): Title of the suggestion.
        description (str): Detailed description of the suggestion.
        type (SuggestionType): Type of the suggestion.
        priority (int): Priority level (1-5, with 5 being highest).
        related_device_ids (Optional[List[str]]): IDs of related devices, if any.
    """
    user_id: str
    title: str
    description: str
    type: SuggestionType
    priority: int = 3  # Default to medium priority
    related_device_ids: Optional[List[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, t: str) -> str:
        """
        Validate suggestion title.

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
        Validate suggestion description.

        Arguments:
            d (str): Description to be validated.

        Returns:
            str: Validated description.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if len(d) < 10:
            raise ValueError("Description must be at least 10 characters long.")
        if len(d) > 1000:
            raise ValueError("Description must be less than 1000 characters long.")

        return d

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, p: int) -> int:
        """
        Validate priority level.

        Arguments:
            p (int): Priority to be validated.

        Returns:
            int: Validated priority.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if p < 1 or p > 5:
            raise ValueError("Priority must be between 1 and 5.")
        return p

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, uid: str) -> str:
        """
        Validate user ID format.

        Arguments:
            uid (str): User ID to be validated.

        Returns:
            str: Validated user ID.

        Raises:
            ValueError: Validation encountered an invalid format.
        """
        try:
            uuid.UUID(uid)
        except ValueError as exc:
            raise ValueError("Invalid user_id format. Must be a valid UUID.") from exc

        return uid

    @field_validator("related_device_ids")
    @classmethod
    def validate_device_ids(cls, devices: Optional[List[str]]) -> Optional[List[str]]:
        """
        Validate device IDs format.

        Arguments:
            devices (Optional[List[str]]): Device IDs to be validated.

        Returns:
            Optional[List[str]]: Validated device IDs.

        Raises:
            ValueError: Validation encountered an invalid format.
        """
        if devices:
            for device_id in devices:
                try:
                    uuid.UUID(device_id)
                except ValueError as exc:
                    raise ValueError(f"Invalid device ID format: {device_id}. Must be a valid UUID.") from exc

        return devices


class SuggestionDB(BaseModel):
    """
    Internal model representing suggestion data in the database.

    Attributes:
        id (str): Unique suggestion identifier.
        user_id (str): ID of the user who receives the suggestion.
        title (str): Title of the suggestion.
        description (str): Detailed description of the suggestion.
        type (SuggestionType): Type of the suggestion.
        priority (int): Priority level (1-5, with 5 being highest).
        status (SuggestionStatus): Current status of the suggestion.
        related_device_ids (Optional[List[str]]): IDs of related devices, if any.
        created (datetime): When the suggestion was created.
        updated (Optional[datetime]): When the suggestion was last updated.
        implemented_date (Optional[datetime]): When the suggestion was implemented.
        user_feedback (Optional[str]): Feedback from the user on the suggestion.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    type: SuggestionType
    priority: int
    status: SuggestionStatus = SuggestionStatus.PENDING
    related_device_ids: Optional[List[str]] = None
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: Optional[datetime] = None
    implemented_date: Optional[datetime] = None
    user_feedback: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SuggestionResponse(BaseModel):
    """
    Model for suggestion data returned in API responses.

    Attributes:
        id (str): Unique suggestion identifier.
        user_id (str): ID of the user who receives the suggestion.
        title (str): Title of the suggestion.
        description (str): Description of the suggestion.
        type (SuggestionType): Type of the suggestion.
        priority (int): Priority level.
        status (SuggestionStatus): Current status of the suggestion.
        created (datetime): When the suggestion was created.
        implemented_date (Optional[datetime]): When the suggestion was implemented, if applicable.
    """
    id: str
    user_id: str
    title: str
    description: str
    type: SuggestionType
    priority: int
    status: SuggestionStatus
    created: datetime
    related_device_ids: Optional[List[str]] = None
    implemented_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SuggestionUpdate(BaseModel):
    """
    Model for updating suggestion information.

    Attributes:
        title (Optional[str]): Updated title.
        description (Optional[str]): Updated description.
        priority (Optional[int]): Updated priority.
        status (Optional[SuggestionStatus]): Updated status.
        related_device_ids (Optional[List[str]]): Updated related device IDs.
        user_feedback (Optional[str]): User feedback on the suggestion.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[SuggestionStatus] = None
    related_device_ids: Optional[List[str]] = None
    user_feedback: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, t: Optional[str]) -> Optional[str]:
        """
        Validate suggestion title.

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
        Validate suggestion description.

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
            if len(d) > 1000:
                raise ValueError("Description must be less than 1000 characters long.")

        return d

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, p: Optional[int]) -> Optional[int]:
        """
        Validate priority level.

        Arguments:
            p (Optional[int]): Priority to be validated.

        Returns:
            Optional[int]: Validated priority.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if isinstance(p, int) and (p < 1 or p > 5):
            raise ValueError("Priority must be between 1 and 5.")

        return p

    @field_validator("user_feedback")
    @classmethod
    def validate_feedback(cls, f: Optional[str]) -> Optional[str]:
        """
        Validate user feedback.

        Arguments:
            f (Optional[str]): Feedback to be validated.

        Returns:
            Optional[str]: Validated feedback.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if isinstance(f, str) and len(f) > 500:
            raise ValueError("Feedback must be less than 500 characters long.")

        return f

    @field_validator("related_device_ids")
    @classmethod
    def validate_device_ids(cls, devices: Optional[List[str]]) -> Optional[List[str]]:
        """
        Validate device IDs format.

        Arguments:
            devices (Optional[List[str]]): Device IDs to be validated.

        Returns:
            Optional[List[str]]: Validated device IDs.

        Raises:
            ValueError: Validation encountered an invalid format.
        """
        if devices:
            for device_id in devices:
                try:
                    uuid.UUID(device_id)
                except ValueError as exc:
                    raise ValueError(f"Invalid device ID format: {device_id}. Must be a valid UUID.") from exc

        return devices
