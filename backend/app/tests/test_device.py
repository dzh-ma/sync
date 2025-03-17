"""
Unit tests for device validation models.
"""
import pytest
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any

from app.models.device import (
    DeviceType,
    DeviceStatus,
    CreateDevice,
    DeviceDB,
    DeviceResponse,
    DeviceUpdate
)

class TestCreateDevice:
    """Tests for the CreateDevice model."""

    def test_valid_device_creation(self):
        """Test that a valid device can be created."""
        device_data = {
            "name": "Living Room Light",
            "type": DeviceType.LIGHT,
            "user_id": str(uuid.uuid4()),
            "room_id": str(uuid.uuid4()),
            "ip_address": "192.168.1.100",
            "mac_address": "00:11:22:33:44:55",
            "manufacturer": "Philips",
            "model": "Hue Color",
            "firmware_version": "1.2.3",
            "settings": {"brightness": 75, "color": "white"}
        }
        
        device = CreateDevice(**device_data)
        
        assert device.name == device_data["name"]
        assert device.type == DeviceType.LIGHT
        assert device.user_id == device_data["user_id"]
        assert device.settings == device_data["settings"]

    def test_minimal_device_creation(self):
        """Test that a device with only required fields can be created."""
        device_data = {
            "name": "Basement Sensor",
            "type": DeviceType.SENSOR,
            "user_id": str(uuid.uuid4())
        }
        
        device = CreateDevice(**device_data)
        
        assert device.name == device_data["name"]
        assert device.type == DeviceType.SENSOR
        assert device.user_id == device_data["user_id"]
        assert device.room_id is None
        assert device.settings is None

    def test_invalid_empty_name(self):
        """Test validation error when name is empty."""
        device_data = {
            "name": "",
            "type": DeviceType.LIGHT,
            "user_id": str(uuid.uuid4())
        }
        
        with pytest.raises(ValueError, match="Device name can't be empty"):
            CreateDevice(**device_data)
            
    def test_invalid_long_name(self):
        """Test validation error when name is too long."""
        device_data = {
            "name": "X" * 101,  # 101 characters, exceeds 100 limit
            "type": DeviceType.LIGHT,
            "user_id": str(uuid.uuid4())
        }
        
        with pytest.raises(ValueError, match="Device name must be less than 100 characters long"):
            CreateDevice(**device_data)

    def test_enum_validation(self):
        """Test that device type validates against the enum."""
        # Valid type
        device = CreateDevice(
            name="Test Device",
            type=DeviceType.THERMOSTAT,
            user_id=str(uuid.uuid4())
        )
        assert device.type == DeviceType.THERMOSTAT
        
        # String matching enum
        device = CreateDevice(
            name="Test Device",
            type="camera",
            user_id=str(uuid.uuid4())
        )
        assert device.type == DeviceType.CAMERA
        
        # Invalid type
        with pytest.raises(ValueError):
            CreateDevice(
                name="Test Device",
                type="invalid_type",
                user_id=str(uuid.uuid4())
            )


class TestDeviceDB:
    """Tests for the DeviceDB model."""
    
    def test_default_values(self):
        """Test that default values are set correctly."""
        user_id = str(uuid.uuid4())
        device_id = str(uuid.uuid4())
        
        device = DeviceDB(
            id=device_id,  # ID is required in your implementation
            name="Test Device",
            type=DeviceType.SWITCH,
            user_id=user_id
        )
        
        assert device.id == device_id
        assert device.name == "Test Device"
        assert device.type == DeviceType.SWITCH
        assert device.user_id == user_id
        assert device.status == DeviceStatus.OFFLINE
        assert device.last_online is None
        assert isinstance(device.created, datetime)
        assert device.updated is None
        assert device.capabilities == []

    def test_create_from_create_device(self):
        """Test creating a DeviceDB instance from a CreateDevice."""
        device_id = str(uuid.uuid4())
        create_data = {
            "name": "Office Light",
            "type": DeviceType.LIGHT,
            "user_id": str(uuid.uuid4()),
            "room_id": str(uuid.uuid4()),
            "manufacturer": "IKEA",
            "settings": {"color_temp": 4000}
        }
        
        create_device = CreateDevice(**create_data)
        
        # In a real app, you'd convert CreateDevice to DeviceDB
        # Adding the required id field
        device_db = DeviceDB(
            id=device_id,
            **create_device.model_dump(),
        )
        
        assert device_db.id == device_id
        assert device_db.name == create_data["name"]
        assert device_db.type == DeviceType.LIGHT
        assert device_db.user_id == create_data["user_id"]
        assert device_db.room_id == create_data["room_id"]
        assert device_db.settings == create_data["settings"]
        assert device_db.status == DeviceStatus.OFFLINE  # Default value


class TestDeviceResponse:
    """Tests for the DeviceResponse model."""
    
    def test_create_from_device_db(self):
        """Test creating a DeviceResponse from a DeviceDB instance."""
        now = datetime.utcnow()
        device_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        room_id = str(uuid.uuid4())
        
        # Create the DeviceDB instance with only fields that are expected in DeviceResponse
        device_db = DeviceDB(
            id=device_id,
            name="Smart Thermostat",
            type=DeviceType.THERMOSTAT,
            user_id=user_id,
            room_id=room_id,
            manufacturer="Nest",
            model="Learning Thermostat",
            status=DeviceStatus.ONLINE,
            last_online=now,
            created=now - timedelta(days=30),
            capabilities=["temperature", "humidity", "scheduling"]
        )
        
        # Create response using model_validate (for Pydantic v2) or construct (for older versions)
        # This approach is less likely to cause validation issues
        response = DeviceResponse.model_validate(device_db.model_dump())
        
        # Check that the right fields are included
        assert response.id == device_id
        assert response.name == "Smart Thermostat"
        assert response.type == DeviceType.THERMOSTAT
        assert response.user_id == user_id
        assert response.room_id == room_id
        assert response.manufacturer == "Nest"
        assert response.model == "Learning Thermostat"
        assert response.status == DeviceStatus.ONLINE
        assert response.last_online == now
        assert response.created == now - timedelta(days=30)
        assert response.capabilities == ["temperature", "humidity", "scheduling"]
        
        # Check that sensitive fields are excluded
        response_dict = response.model_dump()
        assert "ip_address" not in response_dict
        assert "mac_address" not in response_dict
        assert "firmware_version" not in response_dict
        assert "settings" not in response_dict


class TestDeviceUpdate:
    """Tests for the DeviceUpdate model."""
    
    def test_partial_update(self):
        """Test that a partial update can be created."""
        update_data = {
            "name": "Updated Device Name",
            "room_id": str(uuid.uuid4()),
            "status": DeviceStatus.ONLINE
        }
        
        update = DeviceUpdate(**update_data)
        
        assert update.name == update_data["name"]
        assert update.room_id == update_data["room_id"]
        assert update.status == DeviceStatus.ONLINE
        assert update.ip_address is None
        assert update.firmware_version is None
        assert update.settings is None

    def test_settings_update(self):
        """Test updating device settings."""
        settings: Dict[str, Any] = {
            "brightness": 100,
            "color": "blue",
            "power_saving": True
        }
        
        update = DeviceUpdate(settings=settings)
        
        assert update.name is None
        assert update.settings == settings

    def test_invalid_name_update(self):
        """Test validation error when updating with invalid name."""
        # Empty name
        with pytest.raises(ValueError, match="Device name can't be empty"):
            DeviceUpdate(name="")
            
        # Name too long
        with pytest.raises(ValueError, match="Device name must be less than 100 characters long"):
            DeviceUpdate(name="X" * 101)

    def test_apply_update_to_device(self):
        """Test applying an update to a DeviceDB instance."""
        device_id = str(uuid.uuid4())
        
        # Create original device
        device = DeviceDB(
            id=device_id,  # ID is required in your implementation
            name="Original Name",
            type=DeviceType.LOCK,
            user_id=str(uuid.uuid4()),
            room_id=str(uuid.uuid4()),
            status=DeviceStatus.OFFLINE,
            settings={"auto_lock": True}
        )
        
        # Create update
        update_data = {
            "name": "New Device Name",
            "status": DeviceStatus.ONLINE,
            "firmware_version": "2.1.0",
            "settings": {"auto_lock": False, "lock_timeout": 30}
        }
        update = DeviceUpdate(**update_data)
        
        # Apply update (simulating what would happen in a real application)
        update_dict = {k: v for k, v in update.model_dump().items() if v is not None}
        updated_device = DeviceDB(**{**device.model_dump(), **update_dict, "updated": datetime.utcnow()})
        
        # Check that updates were applied
        assert updated_device.id == device.id  # ID stays the same
        assert updated_device.name == "New Device Name"
        assert updated_device.type == DeviceType.LOCK  # Type stays the same
        assert updated_device.user_id == device.user_id  # User stays the same
        assert updated_device.room_id == device.room_id  # Room stays the same
        assert updated_device.status == DeviceStatus.ONLINE
        assert updated_device.firmware_version == "2.1.0"
        assert updated_device.settings == {"auto_lock": False, "lock_timeout": 30}
        assert isinstance(updated_device.updated, datetime)
