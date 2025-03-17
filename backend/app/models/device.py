"""
Model for device validation & storage.
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import user

class DeviceType(str, Enum):
    """
    Enumeration of supported device types.
    """
    LIGHT = "light"
    THERMOSTAT = "thermostat"
    LOCK = "lock"
    CAMERA = "camera"
    SENSOR = "sensor"
    SWITCH = "switch"
    OUTLET = "outlet"
    SPEAKER = "speaker"
    OTHER = "other"


class DeviceStatus(str, Enum):
    """
    Enumeration of possible device statuses.
    """
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class CreateDevice(BaseModel):
    """
    Model for device registration input.

    Attributes:
        name (str): Device name.
        type (DeviceType): Type of device.
        user_id (str): ID of the user who owns the device.
        room_id (Optional[str]): ID of the room where the device is located.
        ip_address (Optional[str]): Device IP address.
        mac_address (Optional[str]): Device MAC address.
        manufacturer (Optional[str]): Device manufacturer.
        model (Optional[str]): Device model.
        firmware_version (Optional[str]): Current firmware version.
        settings (Optional[Dict]): Device-specific settings.
    """
    name: str
    type: DeviceType
    user_id: str
    room_id: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, n: str) -> str:
        """
        Validate device name according to requirements.

        Args:
            name (str): Device name to be validated.

        Returns:
            str: Validated device name.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if len(n) < 1:
            raise ValueError("Device name can't be empty.")
        if len(n) > 100:
            raise ValueError("Device name must be less than 100 characters long.")

        return n


class DeviceDB(BaseModel):
    """
    Internal model representing device data in the database

    Attributes:
        id (str): Unique device identifier.
        name (str): Device name.
        type (DeviceType): Type of device.
        user_id (str): ID of the user who owns the device.
        room_id (Optional[str]): ID of the room where the device is located.
        ip_address (Optional[str]): Device IP address.
        mac_address (Optional[str]): Device MAC address.
        manufacturer (Optional[str]): Device manufacturer.
        model (Optional[str]): Device model.
        firmware_version (Optional[str]): Current firmware version.
        settings (Optional[Dict]): Device-specific settings.
        status (DeviceStatus): Current device status.
        last_online (Optional[datetime]): When the device was last seen online.
        created (datetime): When the device was added to the system.
        updated (Optional[datetime]): When the device data was last updated.
        capabilities (List[str]): List of device capabilities/features.
    """
    id: str
    name: str
    type: DeviceType
    user_id: str
    room_id: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    status: DeviceStatus = DeviceStatus.OFFLINE
    last_online: Optional[datetime] = None
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: Optional[datetime] = None
    capabilities: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class DeviceResponse(BaseModel):
    """
    Model for device data returned in API responses.

    Attributes:
        id (str): Unique device identifier.
        name (str): Device name.
        type (DeviceType): Type of device.
        user_id (str): ID of the user who owns the device.
        room_id (Optional[str]): ID of the room where the device is located.
        manufacturer (Optional[str]): Device manufacturer.
        model (Optional[str]): Device model.
        status (DeviceStatus): Current device status.
        last_online (Optional[datetime]): When the device was last seen online.
        created (datetime): When the device was added to the system.
        capabilities (List[str]): List of device capabilities/features.
    """
    id: str
    name: str
    type: DeviceType
    user_id: str
    room_id: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    status: DeviceStatus
    last_online: Optional[datetime] = None
    created: datetime
    capabilities: List[str] = []


class DeviceUpdate(BaseModel):
    """
    Model for updating device information.

    Attributes:
        name (Optional[str]): Updated device name.
        room_id (Optional[str]): Updated room location.
        ip_address (Optional[str]): Updated IP address.
        firmware_version (Optional[str]): Updated firmware version.
        settings (Optional[Dict]): Updated device settings.
        status (Optional[DeviceStatus]): Updated device status.
    """
    name: Optional[str] = None
    room_id: Optional[str] = None
    ip_address: Optional[str] = None
    firmware_version: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    status: Optional[DeviceStatus] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, n: Optional[str]) -> Optional[str]:
        """
        Validate device name according to requirements.

        Args:
            n (Optional[str]): Device name to be validated.

        Returns: 
            Optional[str]: Validated device name.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if n is None:
            return None

        if len(n) < 1:
            raise ValueError("Device name can't be empty.")
        if len(n) > 100:
            raise ValueError("Device name must be less than 100 characters long.")

        return n
