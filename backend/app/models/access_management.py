"""
Models for access management validation.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ResourceType(str, Enum):
    """
    Enum for supported resource types in the system.
    """
    DEVICE = "device"
    ROOM = "room"
    HOME = "home"
    AUTOMATION = "automation"


class AccessLevel(str, Enum):
    """
    Enum for access permission levels.
    """
    READ = "read"
    CONTROL = "control"
    MANAGE = "manage"
    ADMIN = "admin"

class CreateAccessManagement(BaseModel):
    """
    Model for creating access management entries.

    Attributes:
        owner_id (str): ID of the user who owns the resource.
        resource_id (str): ID of the resource being shared.
        resource_type (ResourceType): Type of resource being shared.
        user_ids (List[str]): List of user IDs to grant access to.
        access_level (AccessLevel): Level of access to grant.
        expires_at (Optional[datetime]): When the access expires (optional).
        note (Optional[str]): Optional note about this access grant.
    """
    owner_id: str
    resource_id: str
    resource_type: ResourceType
    user_ids: List[str]
    access_level: AccessLevel
    expires_at: Optional[datetime] = None
    note: Optional[str] = None

    @field_validator("note")
    @classmethod
    def validate_note(cls, n: Optional[str]) -> Optional[str]:
        """
        Validate note length.

        Arguments:
            n (Optional[str]): Note to validate.

        Returns:
            Optional[str]: Validated note.

        Raises:
            ValueError: If validation fails.
        """
        if n is not None and len(n) > 200:
            raise ValueError("Note must be less than 200 characters long.")

        return n

    @field_validator("user_ids")
    @classmethod
    def validate_user_ids(cls, u: List[str]) -> List[str]:
        """
        Validate user IDs list.

        Arguments:
            u (List[str]): List of user IDs.

        Returns:
            List[str]: Validated list of user IDs.

        Raises:
            ValueError: If validation fails.
        """
        if not u:
            raise ValueError("At least one user ID must be provided.")
        if len(u) > 50:
            raise ValueError("Cannot share with more than 50 users at once.")

        return u


class AccessManagementDB(BaseModel):
    """
    Internal model representing access management data in the database.

    Attributes:
        id (str): Unique identifier.
        owner_id (str): ID of the user who owns the resource.
        resource_id (str): ID of the resource being shared.
        resource_type (ResourceType): Type of resource being shared.
        user_id (str): ID of the user granted access.
        access_level (AccessLevel): Level of access granted.
        created (datetime): When the access was granted.
        updated (Optional[datetime]): When the access was last updated.
        expires_at (Optional[datetime]): When the access expires.
        active (bool): Whether this access grant is currently active.
        note (Optional[str]): Optional note about this access grant.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str
    resource_id: str
    resource_type: ResourceType
    user_id: str
    access_level: AccessLevel
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    active: bool = True
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AccessManagementResponse(BaseModel):
    """
    Model for access management data returned in API responses.

    Attributes:
        id (str): Unique identifier.
        owner_id (str): ID of the user who owns the resource.
        resource_id (str): ID of the resource being shared.
        resource_type (ResourceType): Type of resource being shared.
        user_id (str): ID of the user granted access.
        access_level (AccessLevel): Level of access granted.
        created (datetime): When the access was granted.
        expires_at (Optional[datetime]): When the access expires.
        active (bool): Whether this access grant is currently active.
    """
    id: str
    owner_id: str
    resource_id: str
    resource_type: ResourceType
    user_id: str
    access_level: AccessLevel
    created: datetime
    expires_at: Optional[datetime] = None
    active: bool
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AccessManagementUpdate(BaseModel):
    """
    Model for updating access management entries.

    Attributes:
        access_level (Optional[AccessLevel]): Updated access level.
        expires_at (Optional[datetime]): Updated expiration time.
        active (Optional[bool]): Updated active status.
        note (Optional[str]): Updated note.
    """
    access_level: Optional[AccessLevel] = None
    expires_at: Optional[datetime] = None
    active: Optional[bool] = None
    note: Optional[str] = None

    @field_validator("note")
    @classmethod
    def validate_note(cls, n: Optional[str]) -> Optional[str]:
        """
        Validate note length.

        Arguments:
            n (Optional[str]): Note to validate.

        Returns:
            Optional[str]: Validated note.

        Raises:
            ValueError: If validation fails.
        """
        if n is not None and len(n) > 200:
            raise ValueError("Note must be less than 200 characters long.")

        return n
