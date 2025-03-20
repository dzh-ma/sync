"""
Tests for room routes.
"""
import sys
from pymongo.errors import DuplicateKeyError
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import the app
sys.path.append(".")
from app.main import app
from app.models.user import UserDB

# Initialize test client
client = TestClient(app)

# Mock user data
MOCK_ADMIN = {
    "id": "admin-id-123",
    "username": "admin",
    "email": "admin@example.com",
    "hashed_password": "hashed_password",
    "active": True,
    "verified": True,
    "created": datetime.utcnow(),
    "updated": None,
    "role": "admin"
}

MOCK_USER = {
    "id": "user-id-456",
    "username": "testuser",
    "email": "user@example.com",
    "hashed_password": "hashed_password",
    "active": True,
    "verified": True,
    "created": datetime.utcnow(),
    "updated": None,
    "role": "user"
}

# Mock room data
MOCK_ROOM = {
    "id": "room-id-789",
    "user_id": "user-id-456",
    "home_id": "home-id-123",
    "name": "Living Room",
    "description": "Main living area",
    "type": "living",
    "floor": 1,
    "devices": ["device-id-1", "device-id-2"],
    "created": datetime.utcnow(),
    "updated": None,
    "active": True
}

MOCK_ADMIN_ROOM = {
    "id": "room-id-abc",
    "user_id": "admin-id-123",
    "home_id": "home-id-456",
    "name": "Admin Office",
    "description": "Admin's work space",
    "type": "office",
    "floor": 2,
    "devices": ["device-id-3"],
    "created": datetime.utcnow(),
    "updated": None,
    "active": True
}

# Override auth dependency
from app.core.auth import get_current_user

# Define a simple list-like cursor mock that works with iteration
class MockCursor:
    def __init__(self, items):
        self.items = items
    
    def skip(self, n):
        return self
    
    def limit(self, n):
        return self
    
    def __iter__(self):
        return iter(self.items)


class TestRoomRoutes:
    
    def setup_method(self):
        """Setup for each test."""
        # Set the default auth override to admin
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
    
    def teardown_method(self):
        """Teardown after each test."""
        # Clear any dependency overrides
        app.dependency_overrides.clear()
    
    @patch("app.routes.room_routes.r_c")
    def test_get_all_rooms_as_admin(self, mock_collection):
        """Test getting all rooms as admin."""
        # Setup the mock to return our test rooms
        mock_cursor = MockCursor([MOCK_ROOM, MOCK_ADMIN_ROOM])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        response = client.get("/api/v1/rooms/")
        
        # Verify response
        assert response.status_code == 200
        rooms = response.json()
        assert len(rooms) == 2
        assert rooms[0]["id"] == MOCK_ROOM["id"]
        assert rooms[1]["id"] == MOCK_ADMIN_ROOM["id"]
        
        # Verify the mock was called
        mock_collection.find.assert_called_once()
    
    @patch("app.routes.room_routes.r_c")
    def test_get_all_rooms_as_user(self, mock_collection):
        """Test getting all rooms as regular user."""
        # Set auth override to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock to return our test rooms
        mock_cursor = MockCursor([MOCK_ROOM])  # User should only see their own rooms
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        response = client.get("/api/v1/rooms/")
        
        # Verify response
        assert response.status_code == 200
        rooms = response.json()
        assert len(rooms) == 1
        assert rooms[0]["id"] == MOCK_ROOM["id"]
        
        # Verify the mock was called with correct user filter
        mock_collection.find.assert_called_once()
        query = mock_collection.find.call_args[0][0]  # Get the query argument
        assert query["user_id"] == MOCK_USER["id"]  # Check if user_id is in the query
    
    @patch("app.routes.room_routes.r_c")
    def test_get_room_by_id(self, mock_collection):
        """Test getting a room by ID."""
        # Setup the mock
        mock_collection.find_one.return_value = MOCK_ROOM
        
        # Call the endpoint
        response = client.get(f"/api/v1/rooms/{MOCK_ROOM['id']}")
        
        # Verify response
        assert response.status_code == 200
        room = response.json()
        assert room["id"] == MOCK_ROOM["id"]
        assert room["name"] == MOCK_ROOM["name"]
        assert room["type"] == MOCK_ROOM["type"]
        
        # Verify the mock was called with correct parameters
        mock_collection.find_one.assert_called_once_with({"id": MOCK_ROOM["id"]})
    
    @patch("app.routes.room_routes.r_c")
    def test_get_room_not_found(self, mock_collection):
        """Test getting a room that doesn't exist."""
        # Setup the mock
        mock_collection.find_one.return_value = None
        
        # Call the endpoint
        response = client.get("/api/v1/rooms/nonexistent-id")
        
        # Verify response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @patch("app.routes.room_routes.r_c")
    def test_get_room_unauthorized(self, mock_collection):
        """Test regular user trying to access another user's room."""
        # Set auth override to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock to return admin's room
        mock_collection.find_one.return_value = MOCK_ADMIN_ROOM
        
        # Call the endpoint
        response = client.get(f"/api/v1/rooms/{MOCK_ADMIN_ROOM['id']}")
        
        # Verify response
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    
    @patch("app.routes.room_routes.r_c")
    def test_create_room(self, mock_collection):
        """Test creating a room."""
        # Setup mock for insert_one
        mock_collection.insert_one.return_value = MagicMock()
        
        # Call the endpoint
        new_room_data = {
            "name": "New Room",
            "home_id": "home-id-123",
            "description": "Brand new room",
            "type": "bedroom",
            "floor": 1,
            "devices": []
        }
        response = client.post("/api/v1/rooms/", json=new_room_data)
        
        # Verify response
        assert response.status_code == 201
        room = response.json()
        assert room["name"] == "New Room"
        assert room["home_id"] == "home-id-123"
        assert room["type"] == "bedroom"
        
        # Verify mock calls
        assert mock_collection.insert_one.call_count == 1
        # Verify user_id was set correctly
        insert_call_args = mock_collection.insert_one.call_args[0][0]
        assert insert_call_args["user_id"] == MOCK_ADMIN["id"]
    
    @patch("app.routes.room_routes.r_c")
    def test_create_room_duplicate(self, mock_collection):
        """Test creating a room with duplicate ID."""
        # Setup mock for insert_one to raise DuplicateKeyError
        mock_collection.insert_one.side_effect = DuplicateKeyError("Duplicate key error")
        
        # Call the endpoint
        new_room_data = {
            "name": "Duplicate Room",
            "home_id": "home-id-123",
            "type": "bedroom",
            "floor": 1
        }
        response = client.post("/api/v1/rooms/", json=new_room_data)
        
        # Verify response
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    @patch("app.routes.room_routes.r_c")
    def test_update_room(self, mock_collection):
        """Test updating a room."""
        # Setup the mocks
        mock_collection.find_one.side_effect = [
            MOCK_ROOM,  # First call to find the room
            {**MOCK_ROOM, "name": "Updated Room", "description": "This room has been updated", "updated": datetime.utcnow()}  # Second call to get updated room
        ]
        mock_collection.update_one.return_value.modified_count = 1
        
        # Call the endpoint
        update_data = {
            "name": "Updated Room",
            "description": "This room has been updated"
        }
        response = client.patch(f"/api/v1/rooms/{MOCK_ROOM['id']}", json=update_data)
        
        # Verify response
        assert response.status_code == 200
        room = response.json()
        assert room["name"] == "Updated Room"
        # description is not included in RoomResponse model, so we don't check for it
        
        # Verify mock calls
        assert mock_collection.find_one.call_count == 2
        assert mock_collection.update_one.call_count == 1
        
        # Verify update was called with correct parameters
        update_call_args = mock_collection.update_one.call_args
        assert update_call_args[0][0] == {"id": MOCK_ROOM["id"]}
        assert "name" in update_call_args[0][1]["$set"]
        assert "description" in update_call_args[0][1]["$set"]
        assert "updated" in update_call_args[0][1]["$set"]
    
    @patch("app.routes.room_routes.r_c")
    def test_update_room_not_found(self, mock_collection):
        """Test updating a non-existent room."""
        # Setup the mock
        mock_collection.find_one.return_value = None
        
        # Call the endpoint
        update_data = {"name": "Updated Room"}
        response = client.patch("/api/v1/rooms/nonexistent-id", json=update_data)
        
        # Verify response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @patch("app.routes.room_routes.r_c")
    def test_update_room_unauthorized(self, mock_collection):
        """Test regular user trying to update another user's room."""
        # Set auth override to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock to return admin's room
        mock_collection.find_one.return_value = MOCK_ADMIN_ROOM
        
        # Call the endpoint
        update_data = {"name": "Hacked Room"}
        response = client.patch(f"/api/v1/rooms/{MOCK_ADMIN_ROOM['id']}", json=update_data)
        
        # Verify response
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    
    @patch("app.routes.room_routes.r_c")
    def test_delete_room(self, mock_collection):
        """Test deleting a room."""
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_ROOM
        mock_collection.delete_one.return_value.deleted_count = 1
        
        # Call the endpoint
        response = client.delete(f"/api/v1/rooms/{MOCK_ROOM['id']}")
        
        # Verify response
        assert response.status_code == 204
        assert response.content == b''  # Empty response body for 204
        
        # Verify mock calls
        mock_collection.find_one.assert_called_once_with({"id": MOCK_ROOM["id"]})
        mock_collection.delete_one.assert_called_once_with({"id": MOCK_ROOM["id"]})
    
    @patch("app.routes.room_routes.r_c")
    def test_delete_room_not_found(self, mock_collection):
        """Test deleting a non-existent room."""
        # Setup the mock
        mock_collection.find_one.return_value = None
        
        # Call the endpoint
        response = client.delete("/api/v1/rooms/nonexistent-id")
        
        # Verify response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @patch("app.routes.room_routes.r_c")
    def test_delete_room_unauthorized(self, mock_collection):
        """Test regular user trying to delete another user's room."""
        # Set auth override to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock to return admin's room
        mock_collection.find_one.return_value = MOCK_ADMIN_ROOM
        
        # Call the endpoint
        response = client.delete(f"/api/v1/rooms/{MOCK_ADMIN_ROOM['id']}")
        
        # Verify response
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    
    @patch("app.routes.room_routes.r_c")
    def test_delete_room_failed(self, mock_collection):
        """Test deletion failure in the database."""
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_ROOM
        mock_collection.delete_one.return_value.deleted_count = 0
        
        # Call the endpoint
        response = client.delete(f"/api/v1/rooms/{MOCK_ROOM['id']}")
        
        # Verify response
        assert response.status_code == 500
        assert "Failed to delete" in response.json()["detail"]
    
    @patch("app.routes.room_routes.r_c")
    def test_get_rooms_with_filters(self, mock_collection):
        """Test getting rooms with various filters."""
        # Setup the mock
        mock_cursor = MockCursor([MOCK_ROOM])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint with filters
        response = client.get("/api/v1/rooms/", params={
            "home_id": "home-id-123",
            "type": "living",
            "floor": 1,
            "active": True
        })
        
        # Verify response
        assert response.status_code == 200
        rooms = response.json()
        assert len(rooms) == 1
        
        # Verify the mock was called with correct filters
        mock_collection.find.assert_called_once()
        query = mock_collection.find.call_args[0][0]
        assert query["home_id"] == "home-id-123"
        assert query["type"] == "living"
        assert query["floor"] == 1
        assert query["active"] is True
