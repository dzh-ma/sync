"""
Tests for access management routes.
"""
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Import the app
sys.path.append(".")
from app.main import app
from app.models.user import UserDB
from app.models.access_management import ResourceType, AccessLevel

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

MOCK_OWNER = {
    "id": "owner-id-456",
    "username": "owner",
    "email": "owner@example.com",
    "hashed_password": "hashed_password",
    "active": True,
    "verified": True,
    "created": datetime.utcnow(),
    "updated": None,
    "role": "user"
}

MOCK_USER = {
    "id": "user-id-789",
    "username": "user",
    "email": "user@example.com",
    "hashed_password": "hashed_password",
    "active": True,
    "verified": True,
    "created": datetime.utcnow(),
    "updated": None,
    "role": "user"
}

# Mock access management data
MOCK_ACCESS_1 = {
    "id": "access-id-111",
    "owner_id": MOCK_OWNER["id"],
    "resource_id": "device-id-123",
    "resource_type": ResourceType.DEVICE,
    "user_id": MOCK_USER["id"],
    "access_level": AccessLevel.READ,
    "created": datetime.utcnow(),
    "updated": None,
    "expires_at": datetime.utcnow() + timedelta(days=30),
    "active": True,
    "note": "Shared temperature sensor"
}

MOCK_ACCESS_2 = {
    "id": "access-id-222",
    "owner_id": MOCK_OWNER["id"],
    "resource_id": "room-id-456",
    "resource_type": ResourceType.ROOM,
    "user_id": MOCK_USER["id"],
    "access_level": AccessLevel.CONTROL,
    "created": datetime.utcnow(),
    "updated": None,
    "expires_at": None,
    "active": True,
    "note": "Shared living room"
}

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

# Override auth dependency
from app.core.auth import get_current_user
app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)

class TestAccessManagementRoutes:
    
    @patch("app.routes.access_management_routes.am_c")
    def test_get_all_access_management_as_admin(self, mock_collection):
        """Test getting all access management entries as admin."""
        # Setup the mock to return our test entries
        mock_cursor = MockCursor([MOCK_ACCESS_1, MOCK_ACCESS_2])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        response = client.get("/api/v1/access-management/")
        
        # Verify response
        assert response.status_code == 200
        entries = response.json()
        assert len(entries) == 2
        assert entries[0]["id"] == MOCK_ACCESS_1["id"]
        assert entries[1]["id"] == MOCK_ACCESS_2["id"]
        
        # Verify the mock was called
        mock_collection.find.assert_called_once()
    
    @patch("app.routes.access_management_routes.am_c")
    def test_get_all_access_management_as_owner(self, mock_collection):
        """Test getting access management entries as owner."""
        # Override auth to be the owner
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_OWNER)
        
        try:
            # Setup the mock to return our test entries
            mock_cursor = MockCursor([MOCK_ACCESS_1, MOCK_ACCESS_2])
            mock_collection.find.return_value = mock_cursor
            
            # Call the endpoint
            response = client.get("/api/v1/access-management/")
            
            # Verify response
            assert response.status_code == 200
            entries = response.json()
            assert len(entries) == 2
            
            # Verify the mock was called with owner filter
            # The actual query will include an $or clause with owner_id or user_id
            mock_collection.find.assert_called_once()
            call_args = mock_collection.find.call_args[0][0]
            assert "$or" in call_args
            assert {"owner_id": MOCK_OWNER["id"]} in call_args["$or"]
        finally:
            # Reset auth override
            app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
    
    @patch("app.routes.access_management_routes.am_c")
    def test_get_all_access_management_as_user(self, mock_collection):
        """Test getting access management entries as user with granted access."""
        # Override auth to be the user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        try:
            # Setup the mock to return our test entries
            mock_cursor = MockCursor([MOCK_ACCESS_1, MOCK_ACCESS_2])
            mock_collection.find.return_value = mock_cursor
            
            # Call the endpoint
            response = client.get("/api/v1/access-management/")
            
            # Verify response
            assert response.status_code == 200
            entries = response.json()
            assert len(entries) == 2
            
            # Verify the mock was called with user filter
            mock_collection.find.assert_called_once()
            call_args = mock_collection.find.call_args[0][0]
            assert "$or" in call_args
            assert {"user_id": MOCK_USER["id"]} in call_args["$or"]
        finally:
            # Reset auth override
            app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
    
    @patch("app.routes.access_management_routes.am_c")
    def test_get_access_management_by_id(self, mock_collection):
        """Test getting an access management entry by ID."""
        # Setup the mock
        mock_collection.find_one.return_value = MOCK_ACCESS_1
        
        # Call the endpoint
        response = client.get(f"/api/v1/access-management/{MOCK_ACCESS_1['id']}")
        
        # Verify response
        assert response.status_code == 200
        entry = response.json()
        assert entry["id"] == MOCK_ACCESS_1["id"]
        assert entry["resource_type"] == MOCK_ACCESS_1["resource_type"]
        assert entry["access_level"] == MOCK_ACCESS_1["access_level"]
        
        # Verify the mock was called with correct parameters
        mock_collection.find_one.assert_called_once_with({"id": MOCK_ACCESS_1["id"]})
    
    @patch("app.routes.access_management_routes.am_c")
    def test_get_access_management_by_id_not_found(self, mock_collection):
        """Test getting a non-existent access management entry."""
        # Setup the mock
        mock_collection.find_one.return_value = None
        
        # Call the endpoint
        response = client.get("/api/v1/access-management/nonexistent-id")
        
        # Verify response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @patch("app.routes.access_management_routes.am_c")
    def test_get_access_management_by_id_unauthorized(self, mock_collection):
        """Test unauthorized access to another user's access management."""
        # Create unrelated user
        unrelated_user = {
            "id": "unrelated-id-999",
            "username": "unrelated",
            "email": "unrelated@example.com",
            "hashed_password": "hashed_password",
            "active": True,
            "verified": True,
            "created": datetime.utcnow(),
            "updated": None,
            "role": "user"
        }
        
        # Override auth to be the unrelated user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**unrelated_user)
        
        try:
            # Setup the mock
            mock_collection.find_one.return_value = MOCK_ACCESS_1
            
            # Call the endpoint
            response = client.get(f"/api/v1/access-management/{MOCK_ACCESS_1['id']}")
            
            # Verify response is forbidden
            assert response.status_code == 403
            assert "not authorized" in response.json()["detail"].lower()
        finally:
            # Reset auth override
            app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
    
    @patch("app.routes.access_management_routes.am_c")
    def test_create_access_management(self, mock_collection):
        """Test creating access management entries."""
        # Setup the mock
        mock_collection.insert_one.return_value = MagicMock()
        
        # Call the endpoint
        new_access_data = {
            "owner_id": MOCK_OWNER["id"],
            "resource_id": "device-id-456",
            "resource_type": ResourceType.DEVICE,
            "user_ids": [MOCK_USER["id"]],
            "access_level": AccessLevel.CONTROL,
            "expires_at": (datetime.utcnow() + timedelta(days=60)).isoformat(),
            "note": "Shared thermostat"
        }
        response = client.post("/api/v1/access-management/", json=new_access_data)
        
        # Verify response
        assert response.status_code == 201
        entries = response.json()
        assert len(entries) == 1
        assert entries[0]["resource_id"] == "device-id-456"
        assert entries[0]["access_level"] == AccessLevel.CONTROL
        
        # Verify mock calls
        assert mock_collection.insert_one.call_count == 1
    
    @patch("app.routes.access_management_routes.am_c")
    def test_create_access_management_multiple_users(self, mock_collection):
        """Test creating access management entries for multiple users."""
        # Setup the mock
        mock_collection.insert_one.return_value = MagicMock()
        
        # Call the endpoint with multiple user IDs
        new_access_data = {
            "owner_id": MOCK_OWNER["id"],
            "resource_id": "room-id-789",
            "resource_type": ResourceType.ROOM,
            "user_ids": [MOCK_USER["id"], "another-user-id-123"],
            "access_level": AccessLevel.READ,
            "note": "Shared for viewing only"
        }
        response = client.post("/api/v1/access-management/", json=new_access_data)
        
        # Verify response
        assert response.status_code == 201
        entries = response.json()
        assert len(entries) == 2
        assert entries[0]["resource_id"] == "room-id-789"
        assert entries[1]["resource_id"] == "room-id-789"
        
        # Verify mock calls
        assert mock_collection.insert_one.call_count == 2
    
    @patch("app.routes.access_management_routes.am_c")
    def test_create_access_management_unauthorized(self, mock_collection):
        """Test unauthorized creation of access management entry."""
        # Override auth to be a regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        try:
            # Call the endpoint with a different owner
            new_access_data = {
                "owner_id": MOCK_OWNER["id"],  # Different from MOCK_USER
                "resource_id": "device-id-456",
                "resource_type": ResourceType.DEVICE,
                "user_ids": ["another-user-id"],
                "access_level": AccessLevel.CONTROL
            }
            response = client.post("/api/v1/access-management/", json=new_access_data)
            
            # Verify response is forbidden
            assert response.status_code == 403
            assert "not authorized" in response.json()["detail"].lower()
            
            # Verify mock was not called
            mock_collection.insert_one.assert_not_called()
        finally:
            # Reset auth override
            app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
    
    @patch("app.routes.access_management_routes.am_c")
    def test_update_access_management(self, mock_collection):
        """Test updating an access management entry."""
        # Setup the mocks
        mock_collection.find_one.side_effect = [
            MOCK_ACCESS_1,  # First call (find the entry)
            {**MOCK_ACCESS_1, "access_level": AccessLevel.MANAGE, "note": "Updated note", "updated": datetime.utcnow()}  # Second call (get updated entry)
        ]
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        # Prepare updated data
        update_data = {
            "access_level": AccessLevel.MANAGE,
            "note": "Updated note"
        }
        
        # Call the endpoint
        response = client.patch(f"/api/v1/access-management/{MOCK_ACCESS_1['id']}", json=update_data)
        
        # Verify response
        assert response.status_code == 200
        entry = response.json()
        assert entry["access_level"] == AccessLevel.MANAGE
        assert entry["note"] == "Updated note"
        
        # Verify mock calls
        assert mock_collection.find_one.call_count == 2
        mock_collection.update_one.assert_called_once()
    
    @patch("app.routes.access_management_routes.am_c")
    def test_update_access_management_not_found(self, mock_collection):
        """Test updating a non-existent access management entry."""
        # Setup the mock
        mock_collection.find_one.return_value = None
        
        # Call the endpoint
        update_data = {"access_level": AccessLevel.MANAGE}
        response = client.patch("/api/v1/access-management/nonexistent-id", json=update_data)
        
        # Verify response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @patch("app.routes.access_management_routes.am_c")
    def test_update_access_management_unauthorized(self, mock_collection):
        """Test unauthorized update of access management entry."""
        # Override auth to be a regular user (not the owner)
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        try:
            # Setup the mock
            mock_collection.find_one.return_value = MOCK_ACCESS_1
            
            # Call the endpoint
            update_data = {"access_level": AccessLevel.MANAGE}
            response = client.patch(f"/api/v1/access-management/{MOCK_ACCESS_1['id']}", json=update_data)
            
            # Verify response is forbidden
            assert response.status_code == 403
            assert "not authorized" in response.json()["detail"].lower()
            
            # Verify no update was performed
            mock_collection.update_one.assert_not_called()
        finally:
            # Reset auth override
            app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
    
    @patch("app.routes.access_management_routes.am_c")
    def test_delete_access_management(self, mock_collection):
        """Test deleting an access management entry."""
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_ACCESS_1
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Call the endpoint
        response = client.delete(f"/api/v1/access-management/{MOCK_ACCESS_1['id']}")
        
        # Verify response
        assert response.status_code == 204
        assert response.content == b''  # No content
        
        # Verify mock calls
        mock_collection.find_one.assert_called_once_with({"id": MOCK_ACCESS_1["id"]})
        mock_collection.delete_one.assert_called_once_with({"id": MOCK_ACCESS_1["id"]})
    
    @patch("app.routes.access_management_routes.am_c")
    def test_delete_access_management_not_found(self, mock_collection):
        """Test deleting a non-existent access management entry."""
        # Setup the mock
        mock_collection.find_one.return_value = None
        
        # Call the endpoint
        response = client.delete("/api/v1/access-management/nonexistent-id")
        
        # Verify response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        
        # Verify no deletion was performed
        mock_collection.delete_one.assert_not_called()
    
    @patch("app.routes.access_management_routes.am_c")
    def test_delete_access_management_unauthorized(self, mock_collection):
        """Test unauthorized deletion of access management entry."""
        # Override auth to be a regular user (not the owner)
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        try:
            # Setup the mock
            mock_collection.find_one.return_value = MOCK_ACCESS_1
            
            # Call the endpoint
            response = client.delete(f"/api/v1/access-management/{MOCK_ACCESS_1['id']}")
            
            # Verify response is forbidden
            assert response.status_code == 403
            assert "not authorized" in response.json()["detail"].lower()
            
            # Verify no deletion was performed
            mock_collection.delete_one.assert_not_called()
        finally:
            # Reset auth override
            app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
    
    @patch("app.routes.access_management_routes.am_c")
    def test_delete_fail(self, mock_collection):
        """Test failed deletion of access management entry."""
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_ACCESS_1
        mock_collection.delete_one.return_value = MagicMock(deleted_count=0)
        
        # Call the endpoint
        response = client.delete(f"/api/v1/access-management/{MOCK_ACCESS_1['id']}")
        
        # Verify response
        assert response.status_code == 500
        assert "failed to delete" in response.json()["detail"].lower()
