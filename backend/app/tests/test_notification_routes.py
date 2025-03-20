"""
Test file for notification routes.
"""
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

# Import the app
sys.path.append(".")
from app.main import app
from app.models.user import UserDB
from app.models.notification import NotificationDB

# Initialize test client
client = TestClient(app)

# Mock user data
MOCK_ADMIN = {
    "id": "123e4567-e89b-12d3-a456-426614174000",  # Valid UUID format
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
    "id": "123e4567-e89b-12d3-a456-426614174001",  # Valid UUID format
    "username": "testuser",
    "email": "user@example.com",
    "hashed_password": "hashed_password",
    "active": True,
    "verified": True,
    "created": datetime.utcnow(),
    "updated": None,
    "role": "user"
}

# Mock notification data
MOCK_NOTIFICATION_1 = {
    "id": "123e4567-e89b-12d3-a456-426614174002",  # Valid UUID format
    "user_id": "123e4567-e89b-12d3-a456-426614174001",  # Match MOCK_USER id
    "title": "Test Notification 1",
    "message": "This is a test notification message 1",
    "type": "info",
    "priority": "medium",
    "source": "system",
    "read": False,
    "timestamp": datetime.utcnow(),
    "read_timestamp": None
}

MOCK_NOTIFICATION_2 = {
    "id": "123e4567-e89b-12d3-a456-426614174003",  # Valid UUID format
    "user_id": "123e4567-e89b-12d3-a456-426614174001",  # Match MOCK_USER id
    "title": "Test Notification 2",
    "message": "This is a test notification message 2",
    "type": "alert",
    "priority": "high",
    "source": "device",
    "source_id": "123e4567-e89b-12d3-a456-426614174004",  # Valid UUID format
    "read": True,
    "timestamp": datetime.utcnow(),
    "read_timestamp": datetime.utcnow()
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
    
    def sort(self, field, direction):
        return self
    
    def __iter__(self):
        return iter(self.items)


class TestNotificationRoutes:
    
    @patch("app.routes.notification_routes.n_c")
    def test_get_all_notifications_admin(self, mock_collection):
        """Test getting all notifications as admin."""
        # Override auth dependency for admin
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
        
        # Setup the mock to return our test notifications
        mock_cursor = MockCursor([MOCK_NOTIFICATION_1, MOCK_NOTIFICATION_2])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        response = client.get("/api/v1/notifications/")
        
        # Verify response
        assert response.status_code == 200
        notifications = response.json()
        assert len(notifications) == 2
        assert notifications[0]["id"] == MOCK_NOTIFICATION_1["id"]
        assert notifications[1]["id"] == MOCK_NOTIFICATION_2["id"]
        
        # Verify the mock was called
        mock_collection.find.assert_called_once()
    
    @patch("app.routes.notification_routes.n_c")
    def test_get_all_notifications_user(self, mock_collection):
        """Test getting all notifications as regular user."""
        # Override auth dependency for regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock to return our test notifications
        mock_cursor = MockCursor([MOCK_NOTIFICATION_1, MOCK_NOTIFICATION_2])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        response = client.get("/api/v1/notifications/")
        
        # Verify response
        assert response.status_code == 200
        notifications = response.json()
        assert len(notifications) == 2
        
        # Verify the mock was called with the correct user_id filter
        mock_collection.find.assert_called_once()
        # The first argument to find() should be a query dict with user_id
        query_arg = mock_collection.find.call_args[0][0]
        assert query_arg.get("user_id") == MOCK_USER["id"]
    
    @patch("app.routes.notification_routes.n_c")
    def test_get_notification_by_id(self, mock_collection):
        """Test getting a single notification by ID."""
        # Override auth dependency for regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock
        mock_collection.find_one.return_value = MOCK_NOTIFICATION_1
        
        # Call the endpoint
        response = client.get(f"/api/v1/notifications/{MOCK_NOTIFICATION_1['id']}")
        
        # Verify response
        assert response.status_code == 200
        notification = response.json()
        assert notification["id"] == MOCK_NOTIFICATION_1["id"]
        
        # Verify the mock was called with correct parameters
        mock_collection.find_one.assert_called_once_with({"id": MOCK_NOTIFICATION_1["id"]})
    
    @patch("app.routes.notification_routes.n_c")
    def test_get_notification_unauthorized(self, mock_collection):
        """Test getting a notification that belongs to another user."""
        # Override auth dependency for regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock to return a notification belonging to a different user
        different_user_notification = MOCK_NOTIFICATION_1.copy()
        different_user_notification["user_id"] = "different-user-id"
        mock_collection.find_one.return_value = different_user_notification
        
        # Call the endpoint
        response = client.get(f"/api/v1/notifications/{MOCK_NOTIFICATION_1['id']}")
        
        # Verify response
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
    
    @patch("app.routes.notification_routes.n_c")
    def test_create_notification(self, mock_collection):
        """Test creating a notification."""
        # Override auth dependency for regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup mock for insert_one
        mock_collection.insert_one.return_value = MagicMock()
        
        # Setup mock to bypass UUID validation by patching the validation method
        with patch("app.models.notification.CreateNotification.validate_user_id", return_value=MOCK_USER["id"]):
            # Call the endpoint
            new_notification_data = {
                "user_id": MOCK_USER["id"],
                "title": "New Notification",
                "message": "This is a test message for a new notification",
                "type": "info",
                "priority": "medium",
                "source": "system"
            }
            response = client.post("/api/v1/notifications/", json=new_notification_data)
            
            # Verify response
            assert response.status_code == 201
            notification = response.json()
            assert notification["title"] == "New Notification"
            
            # Verify mock calls
            assert mock_collection.insert_one.call_count == 1
    
    @patch("app.routes.notification_routes.n_c")
    def test_update_notification(self, mock_collection):
        """Test updating a notification."""
        # Override auth dependency for regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock
        mock_collection.find_one.return_value = MOCK_NOTIFICATION_1
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        # Call the endpoint with update data
        update_data = {"read": True}
        response = client.patch(f"/api/v1/notifications/{MOCK_NOTIFICATION_1['id']}", json=update_data)
        
        # Verify response
        assert response.status_code == 200
        
        # Verify the update operation was performed correctly
        mock_collection.update_one.assert_called_once()
        
        # The first argument to update_one should be a query for the notification ID
        query_arg = mock_collection.update_one.call_args[0][0]
        assert query_arg == {"id": MOCK_NOTIFICATION_1["id"]}
        
        # The second argument to update_one should include the update data
        update_arg = mock_collection.update_one.call_args[0][1]["$set"]
        assert "read" in update_arg
        assert update_arg["read"] is True
        assert "read_timestamp" in update_arg  # Should automatically add read_timestamp
    
    @patch("app.routes.notification_routes.n_c")
    def test_bulk_update_notifications(self, mock_collection):
        """Test bulk updating notifications."""
        # Override auth dependency for regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock
        mock_collection.update_many.return_value = MagicMock(modified_count=2, matched_count=2)
        
        # Setup mock to bypass UUID validation by patching the validation method
        with patch("app.models.notification.NotificationBulkUpdate.validate_notification_ids", 
                  return_value=[MOCK_NOTIFICATION_1["id"], MOCK_NOTIFICATION_2["id"]]):
            # Call the endpoint with bulk update data
            bulk_update_data = {
                "notification_ids": [MOCK_NOTIFICATION_1["id"], MOCK_NOTIFICATION_2["id"]],
                "read": True
            }
            response = client.post("/api/v1/notifications/bulk_update", json=bulk_update_data)
            
            # Verify response
            assert response.status_code == 200
            result = response.json()
            assert result["modified_count"] == 2
            assert result["matched_count"] == 2
            
            # Verify the update operation was performed correctly
            mock_collection.update_many.assert_called_once()
            
            # The first argument to update_many should include the notification IDs and user_id
            query_arg = mock_collection.update_many.call_args[0][0]
            assert "id" in query_arg
            assert "$in" in query_arg["id"]
            assert query_arg["id"]["$in"] == bulk_update_data["notification_ids"]
            assert query_arg["user_id"] == MOCK_USER["id"]  # Regular user can only update their own
    
    @patch("app.routes.notification_routes.n_c")
    def test_delete_notification(self, mock_collection):
        """Test deleting a notification."""
        # Override auth dependency for regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock
        mock_collection.find_one.return_value = MOCK_NOTIFICATION_1
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Call the endpoint
        response = client.delete(f"/api/v1/notifications/{MOCK_NOTIFICATION_1['id']}")
        
        # Verify response
        assert response.status_code == 204
        
        # Verify the delete operation was performed
        mock_collection.delete_one.assert_called_once_with({"id": MOCK_NOTIFICATION_1["id"]})
    
    @patch("app.routes.notification_routes.n_c")
    def test_delete_notifications(self, mock_collection):
        """Test deleting multiple notifications."""
        # Override auth dependency for regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock
        mock_collection.delete_many.return_value = MagicMock(deleted_count=2)
        
        # Call the endpoint with query parameters
        response = client.delete("/api/v1/notifications/?read=true")
        
        # Verify response
        assert response.status_code == 204
        
        # Verify the delete operation was performed correctly
        mock_collection.delete_many.assert_called_once()
        
        # The argument to delete_many should include the user_id and read filters
        query_arg = mock_collection.delete_many.call_args[0][0]
        assert query_arg["user_id"] == MOCK_USER["id"]
        assert query_arg["read"] is True

    @patch("app.routes.notification_routes.n_c")
    def test_notification_not_found(self, mock_collection):
        """Test error handling when notification is not found."""
        # Override auth dependency for regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock to return None
        mock_collection.find_one.return_value = None
        
        # Call the endpoint
        response = client.get("/api/v1/notifications/non-existent-id")
        
        # Verify response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def teardown_method(self):
        """Clean up after each test."""
        # Remove the dependency override
        app.dependency_overrides.clear()
