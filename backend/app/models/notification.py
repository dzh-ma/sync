"""
Models for notification validation.
"""
import uuid
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CreateNotification(BaseModel):
    """
    Model for notification creation input.

    Attributes:
        user_id (str): ID of the user to whom the notification belongs.
        title (str): Title of the notification.
        message (str): Content of the notification.
        type (str): Type of notification (e.g., alert, info, warning).
        priority (str): Priority level of the notification.
        source (str): Source of the notification (e.g., device, system).
        source_id (Optional[str]): ID of the source entity (if applicable).
    """
    user_id: str
    title: str
    message: str
    type: Literal["alert", "info", "warning", "success"] = "info"
    priority: Literal["low", "medium", "high"] = "medium"
    source: Literal["device", "system", "automation", "goal", "security"] = "system"
    source_id: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, title: str) -> str:
        """
        Validate the notification title.

        Arguments:
            title (str): Title to be validated.

        Returns:
            str: Validated title.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if len(title) < 3:
            raise ValueError("Title must be at least 3 characters long.")
        if len(title) > 100:
            raise ValueError("Title must be less than 100 characters long.")
        return title

    @field_validator("message")
    @classmethod
    def validate_message(cls, message: str) -> str:
        """
        Validate the notification message.

        Arguments:
            message (str): Message to be validated.

        Returns:
            str: Validated message.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if len(message) < 5:
            raise ValueError("Message must be at least 5 characters long.")
        if len(message) > 1000:
            raise ValueError("Message must be less than 1000 characters long.")
        return message

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, user_id: str) -> str:
        """
        Validate user_id format.

        Arguments:
            user_id (str): User ID to be validated.

        Returns:
            str: Validated user ID.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        try:
            uuid.UUID(user_id)
        except ValueError as v:
            raise ValueError("User ID must be a valid UUID.") from v
        return user_id


class NotificationDB(BaseModel):
    """
    Internal model representing notification data in the database.

    Attributes:
        id (str): Unique notification identifier.
        user_id (str): ID of the user to whom the notification belongs.
        title (str): Title of the notification.
        message (str): Content of the notification.
        type (str): Type of notification.
        priority (str): Priority level of the notification.
        source (str): Source of the notification.
        source_id (Optional[str]): ID of the source entity (if applicable).
        read (bool): Whether the notification has been read.
        timestamp (datetime): When the notification was created.
        read_timestamp (Optional[datetime]): When the notification was read.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    message: str
    type: str
    priority: str
    source: str
    source_id: Optional[str] = None
    read: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    read_timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(BaseModel):
    """
    Model for notification data returned in API responses.

    Attributes:
        id (str): Unique notification identifier.
        user_id (str): ID of the user to whom the notification belongs.
        title (str): Title of the notification.
        message (str): Content of the notification.
        type (str): Type of notification.
        priority (str): Priority level of the notification.
        source (str): Source of the notification.
        source_id (Optional[str]): ID of the source entity (if applicable).
        read (bool): Whether the notification has been read.
        timestamp (datetime): When the notification was created.
        read_timestamp (Optional[datetime]): When the notification was read.
    """
    id: str
    user_id: str
    title: str
    message: str
    type: str
    priority: str
    source: str
    source_id: Optional[str] = None
    read: bool
    timestamp: datetime
    read_timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationUpdate(BaseModel):
    """
    Model for updating notification information.

    Attributes:
        read (Optional[bool]): Updated read status.
        read_timestamp (Optional[datetime]): Updated read timestamp.
    """
    read: Optional[bool] = None
    read_timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class NotificationBulkUpdate(BaseModel):
    """
    Model for bulk updating notifications.

    Attributes:
        notification_ids (list[str]): List of notification IDs to update.
        read (bool): New read status for all specified notifications.
    """
    notification_ids: list[str]
    read: bool = True

    @field_validator("notification_ids")
    @classmethod
    def validate_notification_ids(cls, notification_ids: list[str]) -> list[str]:
        """
        Validate notification IDs format and ensure the list is not empty.

        Arguments:
            notification_ids (list[str]): List of notification IDs to be validated.

        Returns:
            list[str]: Validated list of notification IDs.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if not notification_ids:
            raise ValueError("At least one notification ID must be provided.")
        
        for notification_id in notification_ids:
            try:
                uuid.UUID(notification_id)
            except ValueError:
                raise ValueError(f"Notification ID {notification_id} must be a valid UUID.")
                
        return notification_ids
