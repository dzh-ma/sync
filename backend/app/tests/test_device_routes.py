"""
Tests for device management routes with improved authentication mocking.
"""
import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

from app.routes.device_routes import router as device_router
from app.models.device import DeviceType, DeviceStatus
from app.core.auth import get_current_user

# Create a fresh app for tests to avoid conflicts with main.py
app = FastAPI()

# Override the dependency in the app
def get_test_user():
    """Test override for get_current_user dependency."""
    # This will be dynamically set in the tests
    return get_test_user.user

# Set a default user (to avoid AttributeError)
get_test_user.user = None

# Override the get_current_user dependency
app.dependency_overrides[get_current_user] = get_test_user

# Register the device router with the app
app.include_router(device_router)

# Create test client
client = TestClient(app)

# Mock data with fixed datetime to avoid serialization issues
FIXED_DATETIME = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

# Mock data
MOCK_DEVICE_ID = "device123"
MOCK_USER_ID = "user123"
MOCK_ADMIN_ID = "admin456"
MOCK_ROOM_ID = "room789"

MOCK_DEVICE = {
    "id": MOCK_DEVICE_ID,
    "name": "Test Device",
    "type": DeviceType.LIGHT,
    "user_id": MOCK_USER_ID,
    "room_id": MOCK_ROOM_ID,
    "ip_address": "192.168.1.100",
    "mac_address": "00:11:22:33:44:55",
    "manufacturer": "TestMaker",
    "model": "TestModel",
    "firmware_version": "1.0.0",
    "settings": {"brightness": 80, "color": "white"},
    "status": DeviceStatus.ONLINE,
    "last_online": FIXED_DATETIME,
    "created": FIXED_DATETIME,
    "updated": None,
    "capabilities": ["dimming", "color_changing"]
}

# Create serializable version of the mock device for testing responses
SERIALIZABLE_MOCK_DEVICE = {
    "id": MOCK_DEVICE_ID,
    "name": "Test Device",
    "type": DeviceType.LIGHT.value,  # Use the string value
    "user_id": MOCK_USER_ID,
    "room_id": MOCK_ROOM_ID,
    "manufacturer": "TestMaker",
    "model": "TestModel",
    "status": DeviceStatus.ONLINE.value,  # Use the string value
    "last_online": FIXED_DATETIME.isoformat(),
    "created": FIXED_DATETIME.isoformat(),
    "capabilities": ["dimming", "color_changing"]
}

MOCK_ADMIN_USER = MagicMock(
    id=MOCK_ADMIN_ID,
    username="admin",
    email="admin@example.com",
    role="admin",
    active=True,
    created=FIXED_DATETIME,
    updated=None
)

MOCK_REGULAR_USER = MagicMock(
    id=MOCK_USER_ID,
    username="user",
    email="user@example.com",
    role="user",
    active=True,
    created=FIXED_DATETIME,
    updated=None
)

# Helper decorator for database collection mock
def with_db_mock(test_func):
    """Decorator to mock database collection."""
    from unittest.mock import patch
    
    @patch("app.routes.device_routes.d_c")
    def wrapper(mock_device_collection, *args, **kwargs):
        result = test_func(mock_device_collection, *args, **kwargs)
        return result
    return wrapper

# GET all devices tests
@with_db_mock
def test_get_all_devices_admin(mock_device_collection):
    """Test that an admin can get all devices."""
    # Setup
    get_test_user.user = MOCK_ADMIN_USER
    # Configure the mock to properly return our device
    mock_device_collection.find.return_value = MagicMock()
    mock_device_collection.find.return_value.skip.return_value.limit.return_value = [MOCK_DEVICE]
    
    # Execute
    response = client.get("/devices/")
    
    # Assert
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == MOCK_DEVICE_ID
    # Check that find was called
    mock_device_collection.find.assert_called_once()

@with_db_mock
def test_get_all_devices_user(mock_device_collection):
    """Test that a regular user can only get their own devices."""
    # Setup
    get_test_user.user = MOCK_REGULAR_USER
    # Configure the mock to properly return our device
    mock_device_collection.find.return_value = MagicMock()
    mock_device_collection.find.return_value.skip.return_value.limit.return_value = [MOCK_DEVICE]
    
    # Execute
    response = client.get("/devices/")
    
    # Assert
    assert response.status_code == 200
    # Check that find was called with the correct user_id filter
    mock_device_collection.find.assert_called_once_with({"user_id": MOCK_USER_ID})

@with_db_mock
def test_get_all_devices_with_filters(mock_device_collection):
    """Test getting devices with filters."""
    # Setup
    get_test_user.user = MOCK_ADMIN_USER
    # Configure the mock to properly return our device
    mock_device_collection.find.return_value = MagicMock()
    mock_device_collection.find.return_value.skip.return_value.limit.return_value = [MOCK_DEVICE]
    
    # Execute
    response = client.get(f"/devices/?type={DeviceType.LIGHT.value}&room_id={MOCK_ROOM_ID}")
    
    # Assert
    assert response.status_code == 200
    mock_device_collection.find.assert_called_once()
    args, _ = mock_device_collection.find.call_args
    assert "type" in args[0]
    assert "room_id" in args[0]

# GET specific device tests
@with_db_mock
def test_get_device_admin(mock_device_collection):
    """Test that an admin can get any device."""
    # Setup
    get_test_user.user = MOCK_ADMIN_USER
    mock_device_collection.find_one.return_value = MOCK_DEVICE
    
    # Execute
    response = client.get(f"/devices/{MOCK_DEVICE_ID}")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == MOCK_DEVICE_ID
    mock_device_collection.find_one.assert_called_once_with({"id": MOCK_DEVICE_ID})

@with_db_mock
def test_get_device_owner(mock_device_collection):
    """Test that a device owner can get their device."""
    # Setup
    get_test_user.user = MOCK_REGULAR_USER
    mock_device_collection.find_one.return_value = MOCK_DEVICE
    
    # Execute
    response = client.get(f"/devices/{MOCK_DEVICE_ID}")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == MOCK_DEVICE_ID

@with_db_mock
def test_get_device_unauthorized(mock_device_collection):
    """Test that a non-owner non-admin user cannot get another user's device."""
    # Setup
    unauthorized_user = MagicMock(
        id="unauthorized123",
        username="unauthorized",
        email="unauthorized@example.com",
        role="user"
    )
    get_test_user.user = unauthorized_user
    mock_device_collection.find_one.return_value = MOCK_DEVICE
    
    # Execute
    response = client.get(f"/devices/{MOCK_DEVICE_ID}")
    
    # Assert
    assert response.status_code == 403

@with_db_mock
def test_get_device_not_found(mock_device_collection):
    """Test getting a device that doesn't exist."""
    # Setup
    get_test_user.user = MOCK_ADMIN_USER
    mock_device_collection.find_one.return_value = None
    
    # Execute
    response = client.get("/devices/nonexistent")
    
    # Assert
    assert response.status_code == 404

@with_db_mock
def test_create_device_admin(mock_device_collection):
    """Test that an admin can create a device for any user, including optional fields."""
    # Setup
    get_test_user.user = MOCK_ADMIN_USER
    mock_device_collection.insert_one.return_value = MagicMock()
    
    # Mock the DB "find_one" to return the newly-created device
    mock_device_collection.find_one.return_value = {
        "id": "test-uuid",
        "name": "New Device",
        "type": DeviceType.THERMOSTAT,
        "user_id": MOCK_USER_ID,
        "room_id": MOCK_ROOM_ID,
        "ip_address": "192.168.1.2",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "manufacturer": "TestMaker",
        "model": "AdvancedThermo",
        "firmware_version": "2.0.1",
        "settings": {"mode": "eco"},
        "status": DeviceStatus.OFFLINE,
        "last_online": None,
        "created": FIXED_DATETIME,
        "updated": None,
        "capabilities": []
    }
    
    # Mock the uuid generation
    with patch('uuid.uuid4', return_value='test-uuid'):
        # Supply all the CreateDevice fields, though many are optional
        new_device = {
            "name": "New Device",
            "type": DeviceType.THERMOSTAT.value,  # Use string for JSON
            "user_id": MOCK_USER_ID,
            "room_id": MOCK_ROOM_ID,
            "ip_address": "192.168.1.2",
            "mac_address": "AA:BB:CC:DD:EE:FF",
            "manufacturer": "TestMaker",
            "model": "AdvancedThermo",
            "firmware_version": "2.0.1",
            "settings": {"mode": "eco"}
        }
        
        # Execute
        response = client.post("/devices/", json=new_device)
        
        # Assert
        assert response.status_code == 201
        mock_device_collection.insert_one.assert_called_once()
        created = response.json()
        assert created["id"] == "test-uuid"
        assert created["name"] == "New Device"
        assert created["type"] == DeviceType.THERMOSTAT.value
        assert created["user_id"] == MOCK_USER_ID
        # Check that status defaults to offline if not explicitly set
        assert created["status"] == DeviceStatus.OFFLINE.value

@with_db_mock
def test_create_device_user_for_self(mock_device_collection):
    """Test that a user can create a device for themselves, including optional fields."""
    # Setup
    get_test_user.user = MOCK_REGULAR_USER
    mock_device_collection.insert_one.return_value = MagicMock()
    
    # Mock the DB "find_one" to return the newly-created device
    mock_device_collection.find_one.return_value = {
        "id": "test-uuid",
        "name": "New Device",
        "type": DeviceType.LOCK,
        "user_id": MOCK_USER_ID,
        "room_id": None,
        "ip_address": None,
        "mac_address": None,
        "manufacturer": "LockCorp",
        "model": "Secure1000",
        "firmware_version": None,
        "settings": None,
        "status": DeviceStatus.OFFLINE,
        "last_online": None,
        "created": FIXED_DATETIME,
        "updated": None,
        "capabilities": []
    }
    
    # Mock the uuid generation
    with patch('uuid.uuid4', return_value='test-uuid'):
        # This time we can test that optional fields are omitted if we want
        new_device = {
            "name": "New Device",
            "type": DeviceType.LOCK.value,
            "user_id": MOCK_USER_ID,
            # Omit room_id, ip_address, etc. to confirm defaults work
            "manufacturer": "LockCorp",
            "model": "Secure1000"
        }
        
        # Execute
        response = client.post("/devices/", json=new_device)
        
        # Assert
        assert response.status_code == 201
        mock_device_collection.insert_one.assert_called_once()
        created = response.json()
        assert created["id"] == "test-uuid"
        assert created["name"] == "New Device"
        assert created["type"] == DeviceType.LOCK.value
        assert created["user_id"] == MOCK_USER_ID
        assert created["manufacturer"] == "LockCorp"
        # Check that the optional fields default or remain None
        assert created["room_id"] is None
        assert created["status"] == DeviceStatus.OFFLINE.value

@with_db_mock
def test_create_device_user_for_other(mock_device_collection):
    """Test that a user cannot create a device for another user."""
    # Setup
    get_test_user.user = MOCK_REGULAR_USER
    
    new_device = {
        "name": "New Device",
        "type": DeviceType.THERMOSTAT.value,  # Use string value for JSON
        "user_id": "other_user_id",
        "room_id": MOCK_ROOM_ID,
        "manufacturer": "TestMaker"
    }
    
    # Execute
    response = client.post("/devices/", json=new_device)
    
    # Assert
    assert response.status_code == 403
    mock_device_collection.insert_one.assert_not_called()

@with_db_mock
def test_create_device_duplicate(mock_device_collection):
    """Test creating a device with a duplicate ID."""
    # Setup
    get_test_user.user = MOCK_ADMIN_USER
    mock_device_collection.insert_one.side_effect = DuplicateKeyError("Duplicate key error")
    
    # Mock the uuid generation
    with patch('uuid.uuid4', return_value='test-uuid'):
        new_device = {
            "name": "New Device",
            "type": DeviceType.THERMOSTAT.value,  # Use string value for JSON
            "user_id": MOCK_USER_ID,
            "room_id": MOCK_ROOM_ID,
            "manufacturer": "TestMaker"
        }
        
        # Execute
        response = client.post("/devices/", json=new_device)
        
        # Assert
        assert response.status_code == 400

# PATCH (update) device tests
@with_db_mock
def test_update_device_admin(mock_device_collection):
    """Test that an admin can update any device."""
    # Setup
    get_test_user.user = MOCK_ADMIN_USER
    mock_device_collection.find_one.return_value = MOCK_DEVICE
    mock_device_collection.update_one.return_value = MagicMock(modified_count=1)
    
    update_data = {
        "name": "Updated Device",
        "room_id": "new_room_id"
    }
    
    # Execute
    response = client.patch(f"/devices/{MOCK_DEVICE_ID}", json=update_data)
    
    # Assert
    assert response.status_code == 200
    mock_device_collection.update_one.assert_called_once()

@with_db_mock
def test_update_device_owner(mock_device_collection):
    """Test that a device owner can update their device."""
    # Setup
    get_test_user.user = MOCK_REGULAR_USER
    mock_device_collection.find_one.return_value = MOCK_DEVICE
    mock_device_collection.update_one.return_value = MagicMock(modified_count=1)
    
    update_data = {
        "name": "Updated Device",
        "room_id": "new_room_id"
    }
    
    # Execute
    response = client.patch(f"/devices/{MOCK_DEVICE_ID}", json=update_data)
    
    # Assert
    assert response.status_code == 200
    mock_device_collection.update_one.assert_called_once()

@with_db_mock
def test_update_device_unauthorized(mock_device_collection):
    """Test that a non-owner non-admin user cannot update another user's device."""
    # Setup
    unauthorized_user = MagicMock(
        id="unauthorized123",
        username="unauthorized",
        email="unauthorized@example.com",
        role="user"
    )
    get_test_user.user = unauthorized_user
    mock_device_collection.find_one.return_value = MOCK_DEVICE
    
    update_data = {
        "name": "Updated Device"
    }
    
    # Execute
    response = client.patch(f"/devices/{MOCK_DEVICE_ID}", json=update_data)
    
    # Assert
    assert response.status_code == 403
    mock_device_collection.update_one.assert_not_called()

@with_db_mock
def test_update_device_not_found(mock_device_collection):
    """Test updating a device that doesn't exist."""
    # Setup
    get_test_user.user = MOCK_ADMIN_USER
    mock_device_collection.find_one.return_value = None
    
    update_data = {
        "name": "Updated Device"
    }
    
    # Execute
    response = client.patch("/devices/nonexistent", json=update_data)
    
    # Assert
    assert response.status_code == 404
    mock_device_collection.update_one.assert_not_called()

# DELETE device tests
@with_db_mock
def test_delete_device_admin(mock_device_collection):
    """Test that an admin can delete any device."""
    # Setup
    get_test_user.user = MOCK_ADMIN_USER
    mock_device_collection.find_one.return_value = MOCK_DEVICE
    mock_device_collection.delete_one.return_value = MagicMock(deleted_count=1)
    
    # Execute
    response = client.delete(f"/devices/{MOCK_DEVICE_ID}")
    
    # Assert
    assert response.status_code == 204
    mock_device_collection.delete_one.assert_called_once_with({"id": MOCK_DEVICE_ID})

@with_db_mock
def test_delete_device_owner(mock_device_collection):
    """Test that a device owner can delete their device."""
    # Setup
    get_test_user.user = MOCK_REGULAR_USER
    mock_device_collection.find_one.return_value = MOCK_DEVICE
    mock_device_collection.delete_one.return_value = MagicMock(deleted_count=1)
    
    # Execute
    response = client.delete(f"/devices/{MOCK_DEVICE_ID}")
    
    # Assert
    assert response.status_code == 204
    mock_device_collection.delete_one.assert_called_once_with({"id": MOCK_DEVICE_ID})

@with_db_mock
def test_delete_device_unauthorized(mock_device_collection):
    """Test that a non-owner non-admin user cannot delete another user's device."""
    # Setup
    unauthorized_user = MagicMock(
        id="unauthorized123",
        username="unauthorized",
        email="unauthorized@example.com",
        role="user"
    )
    get_test_user.user = unauthorized_user
    mock_device_collection.find_one.return_value = MOCK_DEVICE
    
    # Execute
    response = client.delete(f"/devices/{MOCK_DEVICE_ID}")
    
    # Assert
    assert response.status_code == 403
    mock_device_collection.delete_one.assert_not_called()

@with_db_mock
def test_delete_device_not_found(mock_device_collection):
    """Test deleting a device that doesn't exist."""
    # Setup
    get_test_user.user = MOCK_ADMIN_USER
    mock_device_collection.find_one.return_value = None
    
    # Execute
    response = client.delete("/devices/nonexistent")
    
    # Assert
    assert response.status_code == 404
    mock_device_collection.delete_one.assert_not_called()

@with_db_mock
def test_delete_device_error(mock_device_collection):
    """Test error handling when device deletion fails."""
    # Setup
    get_test_user.user = MOCK_ADMIN_USER
    mock_device_collection.find_one.return_value = MOCK_DEVICE
    mock_device_collection.delete_one.return_value = MagicMock(deleted_count=0)
    
    # Execute
    response = client.delete(f"/devices/{MOCK_DEVICE_ID}")
    
    # Assert
    assert response.status_code == 500
