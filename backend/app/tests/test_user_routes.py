"""
Minimal test file for user routes.
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


class TestUserRoutes:
    
    @patch("app.routes.user_routes.u_c")
    def test_get_all_users(self, mock_collection):
        """Test getting all users."""
        # Setup the mock to return our test users
        mock_cursor = MockCursor([MOCK_ADMIN, MOCK_USER])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        response = client.get("/api/v1/users/")
        
        # Verify response
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 2
        assert users[0]["id"] == MOCK_ADMIN["id"]
        assert users[1]["id"] == MOCK_USER["id"]
        
        # Verify the mock was called
        mock_collection.find.assert_called_once()
    
    @patch("app.routes.user_routes.u_c")
    def test_get_user_by_id(self, mock_collection):
        """Test getting a user by ID."""
        # Setup the mock
        mock_collection.find_one.return_value = MOCK_USER
        
        # Call the endpoint
        response = client.get(f"/api/v1/users/{MOCK_USER['id']}")
        
        # Verify response
        assert response.status_code == 200
        user = response.json()
        assert user["id"] == MOCK_USER["id"]
        
        # Verify the mock was called with correct parameters
        mock_collection.find_one.assert_called_once_with({"id": MOCK_USER["id"]})
    
    @patch("app.routes.user_routes.u_c")
    def test_create_user(self, mock_collection):
        """Test creating a user."""
        # Setup the mocks
        mock_collection.find_one.return_value = None  # Username and email don't exist
        
        # Call the endpoint
        new_user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123!",
            "role": "user"
        }
        response = client.post("/api/v1/users/", json=new_user_data)
        
        # Verify response
        assert response.status_code == 201
        user = response.json()
        assert user["username"] == "newuser"
        
        # Verify mock calls
        assert mock_collection.find_one.call_count >= 1  # Check username/email
        assert mock_collection.insert_one.call_count == 1  # Insert the user
