"""
This module contains test cases for the room API endpoints

Tested endpoints:
- `/api/v1/rooms/` (Creating rooms)
- `/api/v1/rooms/` (Fetching all rooms)
- `/api/v1/rooms/{room_id}` (Fetching a specific room)
- `/api/v1/rooms/{room_id}` (Updating a room)
- `/api/v1/rooms/{room_id}` (Deleting a room)
- `/api/v1/rooms/{room_id}/devices` (Fetching devices in a room)
"""
from fastapi.testclient import TestClient
from app.main import app
from app.tests.test_report_generation import get_jwt_token
from app.tests.test_profile_routes import get_current_user_id
import uuid

client = TestClient(app)

def test_create_room():
    """
    Test creating a new room.
    
    - Uses an authenticated request
    - Sends a JSON payload with room data
    - Asserts successful creation response
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    room_id = f"test_room_{uuid.uuid4().hex[:8]}"
    
    response = client.post(
        "/api/v1/rooms/",
        json={
            "id": room_id,
            "name": "Test Living Room",
            "created_by": user_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200, f"Failed to create room: {response.json()}"
    assert response.json()["message"] == "Room created successfully"
    assert response.json()["room_id"] == room_id

def test_get_all_rooms():
    """
    Test fetching all rooms.
    
    - Uses an authenticated request
    - Asserts successful response with a list of rooms
    """
    token = get_jwt_token()
    
    response = client.get(
        "/api/v1/rooms/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_room_by_id():
    """
    Test fetching a specific room by ID.
    
    - Uses an authenticated request
    - Asserts successful response with room details
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    room_id = f"test_room_{uuid.uuid4().hex[:8]}"
    
    # First create a room to fetch
    create_response = client.post(
        "/api/v1/rooms/",
        json={
            "id": room_id,
            "name": "Room to Fetch",
            "created_by": user_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Now fetch the room
    response = client.get(
        f"/api/v1/rooms/{room_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == room_id
    assert response.json()["name"] == "Room to Fetch"
    assert response.json()["created_by"] == user_id

def test_update_room():
    """
    Test updating an existing room.
    
    - Uses an authenticated request
    - Sends updated room data
    - Asserts successful update response
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    room_id = f"test_room_{uuid.uuid4().hex[:8]}"
    
    # First create a room to update
    create_response = client.post(
        "/api/v1/rooms/",
        json={
            "id": room_id,
            "name": "Original Room Name",
            "created_by": user_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Now update the room
    response = client.put(
        f"/api/v1/rooms/{room_id}",
        json={
            "id": room_id,
            "name": "Updated Room Name",
            "created_by": user_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Room updated successfully"
    
    # Verify the update
    get_response = client.get(
        f"/api/v1/rooms/{room_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.json()["name"] == "Updated Room Name"

def test_delete_room():
    """
    Test deleting a room.
    
    - Uses an authenticated request
    - Asserts successful deletion response
    - Verifies the room is no longer accessible
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    room_id = f"test_room_{uuid.uuid4().hex[:8]}"
    
    # First create a room to delete
    create_response = client.post(
        "/api/v1/rooms/",
        json={
            "id": room_id,
            "name": "Room to Delete",
            "created_by": user_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Now delete the room
    response = client.delete(
        f"/api/v1/rooms/{room_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Room deleted successfully"
    
    # Verify it's deleted
    get_response = client.get(
        f"/api/v1/rooms/{room_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert get_response.status_code == 404

def test_filter_rooms_by_creator():
    """
    Test filtering rooms by creator.
    
    - Uses an authenticated request
    - Creates rooms by different users
    - Filters by creator and verifies results
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    
    # Create multiple rooms
    for i in range(3):
        room_id = f"creator_test_room_{i}_{uuid.uuid4().hex[:8]}"
        client.post(
            "/api/v1/rooms/",
            json={
                "id": room_id,
                "name": f"Creator Test Room {i}",
                "created_by": user_id
            },
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Filter by creator
    response = client.get(
        f"/api/v1/rooms/?created_by={user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    rooms = response.json()
    creator_rooms = [r for r in rooms if r["id"].startswith("creator_test_room_")]
    for room in creator_rooms:
        assert room["created_by"] == user_id

def test_get_devices_in_room():
    """
    Test getting devices in a specific room.
    
    - Uses an authenticated request
    - Creates a room and adds devices to it
    - Fetches devices in the room and verifies results
    """
    token = get_jwt_token()
    user_id = get_current_user_id(token)
    room_id = f"device_test_room_{uuid.uuid4().hex[:8]}"
    
    # Create a room
    client.post(
        "/api/v1/rooms/",
        json={
            "id": room_id,
            "name": "Device Test Room",
            "created_by": user_id
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Add devices to the room
    for i in range(3):
        client.post(
            "/api/v1/devices/",
            json={
                "id": f"room_device_{i}_{uuid.uuid4().hex[:8]}",
                "name": f"Room Device {i}",
                "type": "light",
                "room_id": room_id,
                "status": "off",
                "is_active": True
            },
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Get devices in the room
    response = client.get(
        f"/api/v1/rooms/{room_id}/devices",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    devices = response.json()
    assert len(devices) >= 3
    for device in devices:
        if device["id"].startswith("room_device_"):
            assert device["room_id"] == room_id
