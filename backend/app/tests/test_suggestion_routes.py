"""
Tests for suggestion routes.
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
from app.models.suggestion import SuggestionStatus, SuggestionType
from app.core.auth import get_current_user

# Use consistent UUIDs for tests
ADMIN_UUID = "a385a273-d71e-4d95-9cea-b6ab1b62124f"
USER_UUID = "b2507612-4512-4480-ad5c-7a9268147c8e"
DEVICE_UUID = "c1a0fafc-65c8-4bfc-bc66-4f129c614e4f"
SUGGESTION_UUID = "d32b5c04-7e13-4b48-b474-32adca6e6db2"

# Mock user data with valid UUIDs
MOCK_ADMIN = {
    "id": ADMIN_UUID,
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
    "id": USER_UUID,
    "username": "testuser",
    "email": "user@example.com",
    "hashed_password": "hashed_password",
    "active": True,
    "verified": True,
    "created": datetime.utcnow(),
    "updated": None,
    "role": "user"
}

# Mock suggestion data
MOCK_SUGGESTION = {
    "id": SUGGESTION_UUID,
    "user_id": USER_UUID,
    "title": "Test Suggestion",
    "description": "This is a test suggestion",
    "type": SuggestionType.ENERGY_SAVING,
    "priority": 3,
    "status": SuggestionStatus.PENDING,
    "related_device_ids": [DEVICE_UUID],
    "created": datetime.utcnow(),
    "updated": None,
    "implemented_date": None,
    "user_feedback": None
}

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


# Fixtures for authentication and client
@pytest.fixture
def admin_client():
    """Return a test client with admin user authentication."""
    app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}  # Clear overrides after test


@pytest.fixture
def user_client():
    """Return a test client with regular user authentication."""
    app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
    client = TestClient(app)
    yield client
    app.dependency_overrides = {}  # Clear overrides after test


# Tests
@patch("app.routes.suggestion_routes.s_c")
def test_get_all_suggestions(mock_collection, admin_client):
    """Test getting all suggestions."""
    # Setup the mock to return our test suggestion
    mock_cursor = MockCursor([MOCK_SUGGESTION])
    mock_collection.find.return_value = mock_cursor
    
    # Call the endpoint
    response = admin_client.get("/api/v1/suggestions/")
    
    # Verify response
    assert response.status_code == 200
    suggestions = response.json()
    assert len(suggestions) == 1
    assert suggestions[0]["id"] == MOCK_SUGGESTION["id"]
    
    # Verify the mock was called
    mock_collection.find.assert_called_once()


@patch("app.routes.suggestion_routes.s_c")
def test_get_suggestion_by_id(mock_collection, admin_client):
    """Test getting a suggestion by ID."""
    # Setup the mock
    mock_collection.find_one.return_value = MOCK_SUGGESTION
    
    # Call the endpoint
    response = admin_client.get(f"/api/v1/suggestions/{MOCK_SUGGESTION['id']}")
    
    # Verify response
    assert response.status_code == 200
    suggestion = response.json()
    assert suggestion["id"] == MOCK_SUGGESTION["id"]
    
    # Verify the mock was called with correct parameters
    mock_collection.find_one.assert_called_once_with({"id": MOCK_SUGGESTION["id"]})


@patch("app.routes.suggestion_routes.s_c")
def test_create_suggestion(mock_collection, admin_client):
    """Test creating a suggestion."""
    # Call the endpoint
    new_suggestion_data = {
        "user_id": USER_UUID,  # Valid UUID from our constants
        "title": "New Suggestion",
        "description": "This is a new suggestion for testing",
        "type": "energy_saving",
        "priority": 4,
        "related_device_ids": [DEVICE_UUID]  # Valid UUID from our constants
    }
    response = admin_client.post("/api/v1/suggestions/", json=new_suggestion_data)
    
    # Verify response
    assert response.status_code == 201
    suggestion = response.json()
    assert suggestion["title"] == "New Suggestion"
    
    # Verify mock calls
    assert mock_collection.insert_one.call_count == 1


@patch("app.routes.suggestion_routes.s_c")
def test_update_suggestion(mock_collection, admin_client):
    """Test updating a suggestion."""
    # Setup the mocks
    mock_collection.find_one.return_value = MOCK_SUGGESTION
    mock_collection.update_one.return_value = MagicMock(modified_count=1)
    
    # Call the endpoint
    update_data = {
        "title": "Updated Suggestion",
        "status": "accepted"
    }
    response = admin_client.patch(f"/api/v1/suggestions/{MOCK_SUGGESTION['id']}", json=update_data)
    
    # Verify response
    assert response.status_code == 200
    
    # Verify mock calls
    mock_collection.find_one.assert_called()
    mock_collection.update_one.assert_called()


@patch("app.routes.suggestion_routes.s_c")
def test_delete_suggestion(mock_collection, admin_client):
    """Test deleting a suggestion."""
    # Setup the mocks
    mock_collection.find_one.return_value = MOCK_SUGGESTION
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
    
    # Call the endpoint
    response = admin_client.delete(f"/api/v1/suggestions/{MOCK_SUGGESTION['id']}")
    
    # Verify response
    assert response.status_code == 204
    
    # Verify mock calls
    mock_collection.find_one.assert_called_once_with({"id": MOCK_SUGGESTION['id']})
    mock_collection.delete_one.assert_called_once_with({"id": MOCK_SUGGESTION['id']})


@patch("app.routes.suggestion_routes.s_c")
def test_get_suggestion_not_found(mock_collection, admin_client):
    """Test getting a non-existent suggestion."""
    # Setup the mock
    mock_collection.find_one.return_value = None
    
    # Call the endpoint
    response = admin_client.get("/api/v1/suggestions/non-existent-id")
    
    # Verify response
    assert response.status_code == 404


@patch("app.routes.suggestion_routes.s_c")
def test_update_suggestion_not_found(mock_collection, admin_client):
    """Test updating a non-existent suggestion."""
    # Setup the mock
    mock_collection.find_one.return_value = None
    
    # Call the endpoint
    update_data = {"title": "Updated Title"}
    response = admin_client.patch("/api/v1/suggestions/non-existent-id", json=update_data)
    
    # Verify response
    assert response.status_code == 404


@patch("app.routes.suggestion_routes.s_c")
def test_delete_suggestion_not_found(mock_collection, admin_client):
    """Test deleting a non-existent suggestion."""
    # Setup the mock
    mock_collection.find_one.return_value = None
    
    # Call the endpoint
    response = admin_client.delete("/api/v1/suggestions/non-existent-id")
    
    # Verify response
    assert response.status_code == 404


@patch("app.routes.suggestion_routes.s_c")
def test_authorization_regular_user(mock_collection, user_client):
    """Test authorization for regular users."""
    # Setup the mock for a suggestion owned by a different user
    different_user_suggestion = MOCK_SUGGESTION.copy()
    different_user_suggestion["user_id"] = "f72c924a-6e62-4e7a-8c3d-d1234f5c98a1"  # Different valid UUID
    mock_collection.find_one.return_value = different_user_suggestion
    
    # Test that the user can't access another user's suggestion
    response = user_client.get(f"/api/v1/suggestions/{different_user_suggestion['id']}")
    assert response.status_code == 403
    
    # Test that the user can't update another user's suggestion
    update_data = {"title": "Updated Title"}
    response = user_client.patch(f"/api/v1/suggestions/{different_user_suggestion['id']}", json=update_data)
    assert response.status_code == 403
    
    # Test that the user can't delete another user's suggestion
    response = user_client.delete(f"/api/v1/suggestions/{different_user_suggestion['id']}")
    assert response.status_code == 403
    
    # Setup the mock for a suggestion owned by the user
    user_suggestion = MOCK_SUGGESTION.copy()
    user_suggestion["user_id"] = MOCK_USER["id"]
    mock_collection.find_one.return_value = user_suggestion
    
    # Test that the user can access their own suggestion
    response = user_client.get(f"/api/v1/suggestions/{user_suggestion['id']}")
    assert response.status_code == 200


@patch("app.routes.suggestion_routes.s_c")
def test_get_suggestions_with_filters(mock_collection, admin_client):
    """Test getting suggestions with filters."""
    # Setup the mock
    mock_cursor = MockCursor([MOCK_SUGGESTION])
    mock_collection.find.return_value = mock_cursor
    
    # Call the endpoint with filters
    response = admin_client.get("/api/v1/suggestions/?status=pending&type=energy_saving&priority=3")
    
    # Verify response
    assert response.status_code == 200
    
    # Verify the mock was called
    mock_collection.find.assert_called_once()
