"""
This module contains test cases for the device API endpoints

Tested endpoints:
- `/api/v1/devices/` (Creating devices)
- `/api/v1/devices/` (Fetching all devices)
- `/api/v1/devices/{device_id}` (Fetching a specific device)
- `/api/v1/devices/{device_id}` (Updating a device)
- `/api/v1/devices/{device_id}` (Deleting a device)
- `/api/v1/devices/{device_id}/toggle` (Toggling device status)
"""
from app.main import app
import json
import uuid
from bson.objectid import ObjectId
from fastapi.testclient import TestClient
from app.tests.test_report_generation import get_jwt_token

client = TestClient(app)

# Helper function to convert ObjectId in responses
def parse_response(response):
    """
    Parse response and convert ObjectId instances to strings
    """
    if hasattr(response, 'json'):
        data = response.json()
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) and '_id' in value:
                    data[key]['_id'] = str(data[key]['_id'])
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and '_id' in item:
                    item['_id'] = str(item['_id'])
        return data
    return response

def test_create_device():
    """
    Test creating a new device.
    
    - Uses an authenticated request
    - Sends a JSON payload with device data
    - Asserts successful creation response
    """
    token = get_jwt_token()
    unique_id = f"test_device_{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/api/v1/devices/",
        json={
            "id": unique_id,
            "name": "Test Device",
            "type": "light",
            "room_id": "living_room",
            "status": "off",
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, f"Failed to create device: {response.json()}"
    assert response.json()["message"] == "Device created successfully"

def test_get_all_devices():
    """
    Test fetching all devices.
    
    - Uses an authenticated request
    - Asserts successful response with a list of devices
    """
    token = get_jwt_token()
    response = client.get(
        "/api/v1/devices/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
def test_get_device_by_id():
    """
    Test fetching a specific device by ID.
    
    - Uses an authenticated request
    - Asserts successful response with device details
    """
    token = get_jwt_token()
    
    # First create a device to fetch
    create_response = client.post(
        "/api/v1/devices/",
        json={
            "id": "test_device_2",
            "name": "Test Device 2",
            "type": "thermostat",
            "room_id": "bedroom",
            "status": "off",
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Now fetch the device
    response = client.get(
        "/api/v1/devices/test_device_2",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == "test_device_2"
    assert response.json()["name"] == "Test Device 2"

def test_update_device():
    """
    Test updating an existing device.
    
    - Uses an authenticated request
    - Sends updated device data
    - Asserts successful update response
    """
    token = get_jwt_token()
    
    # First create a device to update
    create_response = client.post(
        "/api/v1/devices/",
        json={
            "id": "test_device_3",
            "name": "Original Name",
            "type": "light",
            "room_id": "kitchen",
            "status": "off",
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Now update the device
    response = client.put(
        "/api/v1/devices/test_device_3",
        json={
            "id": "test_device_3",
            "name": "Updated Name",
            "type": "light",
            "room_id": "kitchen",
            "status": "on",
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"ACTUAL RESPONSE: {response.json()}")
    
    assert response.status_code == 200
    response_message = response.json()["message"]
    assert response_message in ["Device updated successfully", "No changes applied to the device"]
    
    # Verify the update
    get_response = client.get(
        "/api/v1/devices/test_device_3",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.json()["name"] == "Updated Name"
    assert get_response.json()["status"] == "on"

def test_toggle_device():
    """
    Test toggling a device's status.
    
    - Uses an authenticated request
    - Toggles device status and verifies the change
    """
    token = get_jwt_token()
    
    # First create a device with known status
    create_response = client.post(
        "/api/v1/devices/",
        json={
            "id": "test_device_4",
            "name": "Toggle Test Device",
            "type": "light",
            "room_id": "bedroom",
            "status": "off",
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Toggle the device (off -> on)
    response = client.post(
        "/api/v1/devices/test_device_4/toggle",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "on"
    
    # Toggle again (on -> off)
    response = client.post(
        "/api/v1/devices/test_device_4/toggle",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "off"

def test_delete_device():
    """
    Test deleting a device.
    
    - Uses an admin authenticated request
    - Asserts successful deletion response
    - Verifies the device is no longer accessible
    """
    token = get_jwt_token()  # Assuming this returns an admin token
    
    # First create a device to delete
    create_response = client.post(
        "/api/v1/devices/",
        json={
            "id": "test_device_5",
            "name": "Device to Delete",
            "type": "light",
            "room_id": "living_room",
            "status": "off",
            "is_active": True
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Now delete the device
    response = client.delete(
        "/api/v1/devices/test_device_5",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Device and related data deleted successfully"
    
    # Verify it's deleted
    get_response = client.get(
        "/api/v1/devices/test_device_5",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.status_code == 404

def test_filter_devices_by_room():
    """
    Test filtering devices by room.
    
    - Uses an authenticated request
    - Creates devices in specific rooms
    - Filters by room and verifies results
    """
    token = get_jwt_token()
    
    # Create devices in different rooms
    rooms = ["living_room", "bedroom", "kitchen"]
    for i, room in enumerate(rooms):
        client.post(
            "/api/v1/devices/",
            json={
                "id": f"room_test_device_{i}",
                "name": f"Room Test Device {i}",
                "type": "light",
                "room_id": room,
                "status": "off",
                "is_active": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Filter by the living room
    response = client.get(
        "/api/v1/devices/?room_id=living_room",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    devices = response.json()
    for device in devices:
        if device["id"].startswith("room_test_device_"):
            assert device["room_id"] == "living_room"

def test_filter_devices_by_type():
    """
    Test filtering devices by type.
    
    - Uses an authenticated request
    - Creates devices of different types
    - Filters by type and verifies results
    """
    token = get_jwt_token()
    
    # Create devices of different types
    types = ["light", "thermostat", "appliance"]
    for i, device_type in enumerate(types):
        client.post(
            "/api/v1/devices/",
            json={
                "id": f"type_test_device_{i}",
                "name": f"Type Test Device {i}",
                "type": device_type,
                "room_id": "living_room",
                "status": "off",
                "is_active": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Filter by thermostat type
    response = client.get(
        "/api/v1/devices/?type=thermostat",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    devices = response.json()
    for device in devices:
        if device["id"].startswith("type_test_device_"):
            assert device["type"] == "thermostat"
