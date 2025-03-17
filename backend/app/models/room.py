"""
Models for room validation.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator

class CreateRoom(BaseModel):
    """
    Model for room creation input.

    Attributes:
        name (str): Room's name.
        home_id (str): ID of the home this room belongs to.
        description (Optional[str]): Optional description of the room.
        type (str): Type of room (e.g., bedroom, kitchen, living room).
        floor (int): Floor number where the room is located.
        devices (Optional[List[str]]): List of device IDs in this room.
    """
    name: str
    home_id: str
    description: Optional[str] = None
    type: str
    floor: int = 1  # Default to first floor
    devices: Optional[List[str]] = []

    @field_validator("name")
    @classmethod
    def validate_name(cls, n: str) -> str:
        """
        Validate room name according to requirements.

        Arguments:
            n (str): Room name to be validated.

        Returns:
            str: Validated room name.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if len(n) < 2:
            raise ValueError("Room name must be at least 2 characters long.")
        if len(n) > 50:
            raise ValueError("Room name must be less than 50 characters long.")

        return n

    @field_validator("floor")
    @classmethod
    def validate_floor(cls, f: int) -> int:
        """
        Validate floor number.

        Arguments:
            f (int): Floor number to be validated.

        Returns:
            int: Validated floor number.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if f < -5:  # Allow for basement floors
            raise ValueError("Floor number cannot be less than -5.")
        if f > 200:  # Allow for very tall buildings
            raise ValueError("Floor number cannot be greater than 200.")

        return f


# What gets stored in MongoDB
class RoomDB(BaseModel):
    """
    Internal model representing room data in the database.

    Attributes:
        id (str): Unique room identifier.
        user_id (str): ID of the user who owns this room.
        home_id (str): ID of the home this room belongs to.
        name (str): Room name.
        description (Optional[str]): Optional description of the room.
        type (str): Type of room.
        floor (int): Floor number where the room is located.
        devices (List[str]): List of device IDs in this room.
        created (datetime): When the room was created.
        updated (Optional[datetime]): When the room was last updated.
        active (bool): Whether the room is currently active.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    home_id: str
    name: str
    description: Optional[str] = None
    type: str
    floor: int = 1
    devices: List[str] = []
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: Optional[datetime] = None
    active: bool = True

    model_config = ConfigDict(from_attributes=True)


# What gets returned in API responses
class RoomResponse(BaseModel):
    """
    Model for room data returned in API responses.

    Attributes:
        id (str): Unique room identifier.
        name (str): Room name.
        home_id (str): ID of the home this room belongs to.
        type (str): Type of room.
        floor (int): Floor number where the room is located.
        devices (List[str]): List of device IDs in this room.
        created (datetime): When the room was created.
    """
    id: str
    name: str
    home_id: str
    type: str
    floor: int
    devices: List[str] = []
    created: datetime

    model_config = ConfigDict(from_attributes=True)


# For updating room information
class RoomUpdate(BaseModel):
    """
    Model for updating room information.

    Attributes:
        name (Optional[str]): Updated room name.
        description (Optional[str]): Updated room description.
        type (Optional[str]): Updated room type.
        floor (Optional[int]): Updated floor number.
        devices (Optional[List[str]]): Updated list of device IDs.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    floor: Optional[int] = None
    devices: Optional[List[str]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, n: Optional[str]) -> Optional[str]:
        """
        Validate room name according to requirements.

        Arguments:
            n (Optional[str]): Room name to be validated.

        Returns:
            Optional[str]: Validated room name.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if isinstance(n, str):
            if len(n) < 2:
                raise ValueError("Room name must be at least 2 characters long.")
            if len(n) > 50:
                raise ValueError("Room name must be less than 50 characters long.")

        return n

    @field_validator("floor")
    @classmethod
    def validate_floor(cls, f: Optional[int]) -> Optional[int]:
        """
        Validate floor number.

        Arguments:
            f (Optional[int]): Floor number to be validated.

        Returns:
            Optional[int]: Validated floor number.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if isinstance(f, int):
            if f < -5:
                raise ValueError("Floor number cannot be less than -5.")
            if f > 200:
                raise ValueError("Floor number cannot be greater than 200.")

        return f
