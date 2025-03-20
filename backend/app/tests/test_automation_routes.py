"""
Tests for automation routes.
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

# Mock automation data
MOCK_AUTOMATION_USER = {
    "id": "automation-id-789",
    "name": "Night Mode",
    "description": "Turn off lights at night",
    "user_id": MOCK_USER["id"],
    "device_id": "device-id-123",
    "enabled": True,
    "trigger_type": "time",  # String value of TriggerType.TIME
    "trigger_data": {"time": "22:00:00"},
    "action_type": "device_control",  # String value of ActionType.DEVICE_CONTROL
    "action_data": {"command": "turn_off"},
    "conditions": [{"type": "time_range", "start": "22:00:00", "end": "06:00:00"}],
    "created": datetime.utcnow(),
    "updated": None,
    "last_triggered": None,
    "execution_count": 0
}

MOCK_AUTOMATION_ADMIN = {
    "id": "automation-id-101",
    "name": "Morning Mode",
    "description": "Turn on lights in the morning",
    "user_id": MOCK_ADMIN["id"],
    "device_id": "device-id-456",
    "enabled": True,
    "trigger_type": "time",  # String value of TriggerType.TIME
    "trigger_data": {"time": "06:00:00"},
    "action_type": "device_control",  # String value of ActionType.DEVICE_CONTROL
    "action_data": {"command": "turn_on"},
    "conditions": None,
    "created": datetime.utcnow(),
    "updated": None,
    "last_triggered": None,
    "execution_count": 0
}

# Override auth dependency
from app.core.auth import get_current_user
app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)

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


class TestAutomationRoutes:
    
    @patch("app.routes.automation_routes.a_c")
    def test_get_all_automations(self, mock_collection):
        """Test getting all automations."""
        # Setup the mock to return our test automations
        mock_cursor = MockCursor([MOCK_AUTOMATION_ADMIN, MOCK_AUTOMATION_USER])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        response = client.get("/api/v1/automations/")
        
        # Verify response
        assert response.status_code == 200
        automations = response.json()
        assert len(automations) == 2
        assert automations[0]["id"] == MOCK_AUTOMATION_ADMIN["id"]
        assert automations[1]["id"] == MOCK_AUTOMATION_USER["id"]
        
        # Verify the mock was called
        mock_collection.find.assert_called_once()
    
    @patch("app.routes.automation_routes.a_c")
    def test_get_automation_by_id(self, mock_collection):
        """Test getting an automation by ID."""
        # Setup the mock
        mock_collection.find_one.return_value = MOCK_AUTOMATION_USER
        
        # Call the endpoint
        response = client.get(f"/api/v1/automations/{MOCK_AUTOMATION_USER['id']}")
        
        # Verify response
        assert response.status_code == 200
        automation = response.json()
        assert automation["id"] == MOCK_AUTOMATION_USER["id"]
        
        # Verify the mock was called with correct parameters
        mock_collection.find_one.assert_called_once_with({"id": MOCK_AUTOMATION_USER["id"]})
    
    @patch("app.routes.automation_routes.a_c")
    def test_create_automation(self, mock_collection):
        """Test creating an automation."""
        # Setup the mocks
        mock_collection.insert_one.return_value = None  # Just need this to not error
        
        # Call the endpoint
        new_automation_data = {
            "name": "Test Automation",
            "description": "A test automation",
            "user_id": MOCK_USER["id"],
            "device_id": "device-id-test",
            "enabled": True,
            "trigger_type": "time",  # String value
            "trigger_data": {"time": "12:00:00"},
            "action_type": "notification",  # String value
            "action_data": {"message": "Test notification"}
        }
        response = client.post("/api/v1/automations/", json=new_automation_data)
        
        # Verify response
        assert response.status_code == 201
        automation = response.json()
        assert automation["name"] == "Test Automation"
        
        # Verify mock calls
        assert mock_collection.insert_one.call_count == 1  # Insert the automation
    
    @patch("app.routes.automation_routes.a_c")
    def test_update_automation(self, mock_collection):
        """Test updating an automation."""
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_AUTOMATION_USER
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        # Call the endpoint
        update_data = {
            "name": "Updated Automation",
            "enabled": False
        }
        response = client.patch(f"/api/v1/automations/{MOCK_AUTOMATION_USER['id']}", json=update_data)
        
        # Verify response
        assert response.status_code == 200
        
        # Verify mock calls
        assert mock_collection.find_one.call_count >= 1  # Check automation exists
        assert mock_collection.update_one.call_count == 1  # Update the automation
    
    @patch("app.routes.automation_routes.a_c")
    def test_delete_automation(self, mock_collection):
        """Test deleting an automation."""
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_AUTOMATION_USER
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Call the endpoint
        response = client.delete(f"/api/v1/automations/{MOCK_AUTOMATION_USER['id']}")
        
        # Verify response
        assert response.status_code == 204
        
        # Verify mock calls
        assert mock_collection.find_one.call_count == 1  # Check automation exists
        assert mock_collection.delete_one.call_count == 1  # Delete the automation
        mock_collection.delete_one.assert_called_once_with({"id": MOCK_AUTOMATION_USER["id"]})
    
    @patch("app.routes.automation_routes.a_c")
    def test_user_cannot_access_other_automation(self, mock_collection):
        """Test that a user cannot access another user's automation."""
        # Override auth dependency to use a regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock
        mock_collection.find_one.return_value = MOCK_AUTOMATION_ADMIN  # Admin's automation
        
        # Call the endpoint
        response = client.get(f"/api/v1/automations/{MOCK_AUTOMATION_ADMIN['id']}")
        
        # Verify response
        assert response.status_code == 403
        
        # Restore admin user for other tests
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
    
    @patch("app.routes.automation_routes.a_c")
    def test_filtering_automations(self, mock_collection):
        """Test filtering automations by different parameters."""
        # Setup the mock
        mock_cursor = MockCursor([MOCK_AUTOMATION_USER])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint with filters
        response = client.get(
            "/api/v1/automations/",
            params={
                "user_id": MOCK_USER["id"],
                "device_id": "device-id-123",
                "trigger_type": "time",
                "action_type": "device_control",
                "enabled": "true"
            }
        )
        
        # Verify response
        assert response.status_code == 200
        
        # Verify that find was called with the correct query
        expected_query = {
            "user_id": MOCK_USER["id"],
            "device_id": "device-id-123",
            "trigger_type": "time",
            "action_type": "device_control",
            "enabled": True
        }
        # Check that the query contains all expected items
        actual_query = mock_collection.find.call_args[0][0]
        for key, value in expected_query.items():
            assert key in actual_query
            assert actual_query[key] == value
