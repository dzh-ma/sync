"""
Model for user profile validation & handling.
"""
import uuid
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class CreateProfile(BaseModel):
    """
    Model for creating a new user profile.

    Attributes:
        user_id (str): User identification.
        first_name (str): User's first name.
        last_name (str): User's last name.
        display_name (Optional[str]): User's display name.
        avatar (Optional[str]): URL to user's avatar image.
        phone_number (Optional[str]): User's phone number.
        timezone (str): User's timezone, defaults to UTC.
        temperature_unit (str): Preferred temperature unit (C/F).
        dark_mode (bool): UI theme preference.
    """
    user_id: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: str = "UTC"
    temperature_unit: str = "C"
    dark_mode: bool = False

    @field_validator("temperature_unit")
    @classmethod
    def validate_temp_unit(cls, u: str) -> str:
        """
        Validate temperature unit is either C(elsius) or F(ahrenheit).

        Args:
            u (str): Temperature unit.

        Raises:
            ValueError: Value must either be C or F.
        """
        if u not in ["C", "F"]:
            raise ValueError("Temperature unit must be either `C` or `F`.")

        return u

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, t: str) -> str:
        """
        Basic timezone validation.

        Args:
            t (str): User's timezone.

        Raises:
            ValueError: User's timezone isn't valid.
        """
        if not t:
            raise ValueError("Timezone can't be empty.")

        return t

class ProfileDB(BaseModel):
    """
    Internal model representing profile data in the database.

    Attributes:
        id (str): Unique profile identifier.
        user_id (str): Unique associated user ID.
        first_name (str): User's first name.
        last_name (str): User's last name.
        display_name (Optional[str]): User's display name.
        avatar (Optional[str]): URL to user's avatar image.
        phone_number (Optional[str]): User's phone number.
        timezone (str): User's timezone, defaults to UTC.
        temperature_unit (str): Preferred temperature unit (C/F).
        dark_mode (bool): UI theme preference.
        favorite_devices (List[str]): IDs of favorite devices.
        created (datetime): Profile creation timestamp.
        updated (Optional[datetime]): Last update timestamp.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: str = "UTC"
    temperature_unit: str = "C"
    dark_mode: bool = False
    favorite_devices: List[str] = Field(default_factory=list)
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    """
    Model for profile data returned in API responses.

    Attributes:
        id (str): Unique profile identifier.
        user_id (str): Associated user ID.
        first_name (str): User's first name.
        last_name (str): User's last name.
        display_name (Optional[str]): User's display name.
        avatar (Optional[str]): URL to user's avatar image.
        timezone (str): User's timezone.
        temperature_unit (str): Preferred temperature unit.
        dark_mode (bool): UI theme preference.
        favorite_devices (List[str]): IDs of favorite devices.
    """
    id: str
    user_id: str
    first_name: str
    last_name: str
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    timezone: str
    temperature_unit: str
    dark_mode: bool
    favorite_devices: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    """
    Model for updating profile information.

    All fields are optional since updates may only change some fields.

    Attributes:
        first_name (Optional[str]): User's first name.
        last_name (Optional[str]): User's last name.
        display_name (Optional[str]): User's display name.
        avatar (Optional[str]): URL to user's avatar image.
        phone_number (Optional[str]): User's phone number.
        timezone (Optional[str]): User's timezone.
        temperature_unit (Optional[str]): Preferred temperature unit.
        dark_mode (Optional[bool]): UI theme preference.
        favorite_devices (Optional[List[str]]): IDs of favorite devices.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: Optional[str] = None
    temperature_unit: Optional[str] = None
    dark_mode: Optional[bool] = None
    favorite_devices: Optional[List[str]] = None

    @field_validator("temperature_unit")
    @classmethod
    def validate_temp_unit(cls, u: Optional[str]) -> Optional[str]:
        """
        Validate temperature unit is getting C or F if provided.

        Args:
            u (Optional[str]): Temperature unit.

        Raises:
            ValueError: If temperature unit isn't valid.
        """
        if u is not None and u not in ["C", "F"]:
            raise ValueError("Temperature unit must either be `C` or `F`.")

        return u

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, t: Optional[str]) -> Optional[str]:
        """
        Basic timezone validation if provided.

        Args:
            t (Optional[str]): User's timezone.

        Raises:
            ValueError: If timezone isn't valid.
        """
        if t == "":
            raise ValueError("Timezone can't be an empty string")

        return t
