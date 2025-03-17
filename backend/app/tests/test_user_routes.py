"""
Unit tests for user routes.
"""
import sys
import pytest
import base64
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pymongo.collection import Collection
from datetime import datetime
import uuid

# Import the app and dependencies
sys.path.append(".")  # Add the root directory to the path
from app.main import app
from app.models.user import UserDB, UserResponse, CreateUser

# Initialize test client
client = TestClient(app)

# Mock user data
MOCK_ADMIN_USER = {
    "id": "admin-id-123",
    "username": "admin",
    "email": "admin@example.com",
    "hashed_password": "$2b$12$SvMlbQmI3oOhMmJNlgo6a.A2W3KgYABOVBPkQnES6J.QkLk2tXWNm",  # "password123"
    "active": True,
    "verified": True,
    "created": datetime.utcnow(),
    "updated": None,
    "role": "admin"
}

MOCK_REGULAR_USER = {
    "id": "user-id-456",
    "username": "testuser",
    "email": "user@example.com",
    "hashed_password": "$2b$12$SvMlbQmI3oOhMmJNlgo6a.A2W3KgYABOVBPkQnES6J.QkLk2tXWNm",  # "password123"
    "active": True,
    "verified": True,
    "created": datetime.utcnow(),
    "updated": None,
    "role": "user"
}

SAMPLE_USERS = [MOCK_ADMIN_USER, MOCK_REGULAR_USER]

# Override the dependency for testing - IMPORTANT: Use the correct import path
from app.core.auth import get_current_user

# Create a test user dependency
def override_get_current_user():
    """Override for the get_current_user dependency - returns admin by default."""
    return UserDB(**MOCK_ADMIN_USER)

# Apply the override
app.dependency_overrides[get_current_user] = override_get_current_user

# Helper function to create Basic Auth header (not needed with dependency override)
def get_auth_header(username, password):
    """Create Basic Auth header."""
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded_credentials}"}


# Mock MongoDB for testing
@pytest.fixture(autouse=True)
def mock_db_collection():
    """Mock the MongoDB user collection."""
    with patch("app.db.data.u_c") as mock_collection:
        # Create a proper cursor mock with skip and limit methods
        cursor_mock = MagicMock()
        cursor_mock.skip.return_value = cursor_mock
        cursor_mock.limit.return_value = cursor_mock
        
        # This is the problematic part - should be iterable, not just return SAMPLE_USERS directly
        # Fix: Make the cursor iterable to return SAMPLE_USERS
        cursor_mock.__iter__.return_value = iter(SAMPLE_USERS)
        
        # Configure the mock collection
        mock_collection.find.return_value = cursor_mock
        
        # ISSUE #2: The find_one mock isn't handling MongoDB query format correctly
        # MongoDB often uses {"_id": id} or {"$or": [{"_id": id}, {"username": username}]}
        def mock_find_one(query):
            """Improved mock for find_one that handles various MongoDB query patterns."""
            # Handle _id query which is common in MongoDB
            if "_id" in query:
                user_id = query["_id"]
                for user in SAMPLE_USERS:
                    if user["id"] == user_id:
                        return user
                return None
                
            # Handle id query (your implementation might use this)
            if "id" in query:
                user_id = query["id"]
                for user in SAMPLE_USERS:
                    if user["id"] == user_id:
                        return user
                return None
                
            # Handle username query
            if "username" in query:
                username = query["username"]
                for user in SAMPLE_USERS:
                    if user["username"] == username:
                        return user
                return None
                
            # Handle email query
            if "email" in query:
                email = query["email"]
                for user in SAMPLE_USERS:
                    if user["email"] == email:
                        return user
                return None
                
            # Handle $or queries which are common in MongoDB
            if "$or" in query:
                for condition in query["$or"]:
                    result = mock_find_one(condition)
                    if result:
                        return result
                return None
                
            return None
        
        mock_collection.find_one.side_effect = mock_find_one
        
        # Setup insert_one with a mock response
        insert_mock = MagicMock()
        insert_mock.inserted_id = "new-id-123"
        mock_collection.insert_one.return_value = insert_mock
        
        # Setup update_one with a mock response
        update_mock = MagicMock()
        update_mock.modified_count = 1
        mock_collection.update_one.return_value = update_mock
        
        # Setup delete_one with a mock response
        delete_mock = MagicMock()
        delete_mock.deleted_count = 1
        mock_collection.delete_one.return_value = delete_mock
        
        yield mock_collection


# Test cases
class TestUserRoutes:
    """Tests for user routes."""
    
    def test_get_all_users_as_admin(self, mock_db_collection):
        """Test GET /users/ as admin."""
        # Execute
        response = client.get("/api/v1/users/")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # There should be 2 users in the response
        
        # Verify correct calls
        mock_db_collection.find.assert_called()
    
    def test_get_all_users_as_regular_user(self, mock_db_collection):
        """Test GET /users/ as regular user (should be forbidden)."""
        # Setup - temporarily override to return regular user
        original_override = app.dependency_overrides[get_current_user]
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_REGULAR_USER)
        
        try:
            # Execute
            response = client.get("/api/v1/users/")
            
            # Verify
            assert response.status_code == 403  # Forbidden
        finally:
            # Restore original override
            app.dependency_overrides[get_current_user] = original_override
    
    def test_get_own_user_profile(self, mock_db_collection):
        """Test GET /users/{user_id} for own profile."""
        # Setup - temporarily override to return regular user
        original_override = app.dependency_overrides[get_current_user]
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_REGULAR_USER)
        
        try:
            # Execute
            response = client.get(f"/api/v1/users/{MOCK_REGULAR_USER['id']}")
            
            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == MOCK_REGULAR_USER["id"]
        finally:
            # Restore original override
            app.dependency_overrides[get_current_user] = original_override
    
    def test_get_other_user_profile_as_regular_user(self, mock_db_collection):
        """Test GET /users/{user_id} for another user's profile as regular user (should be forbidden)."""
        # Setup - temporarily override to return regular user
        original_override = app.dependency_overrides[get_current_user]
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_REGULAR_USER)
        
        try:
            # Execute
            response = client.get(f"/api/v1/users/{MOCK_ADMIN_USER['id']}")
            
            # Verify
            assert response.status_code == 403  # Forbidden
        finally:
            # Restore original override
            app.dependency_overrides[get_current_user] = original_override
    
    def test_get_other_user_profile_as_admin(self, mock_db_collection):
        """Test GET /users/{user_id} for another user's profile as admin."""
        # Execute
        response = client.get(f"/api/v1/users/{MOCK_REGULAR_USER['id']}")
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == MOCK_REGULAR_USER["id"]
    
    def test_create_user_as_admin(self, mock_db_collection):
        """Test POST /users/ as admin."""
        # Execute
        new_user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "role": "user"
        }
        response = client.post("/api/v1/users/", json=new_user_data)
        
        # Verify
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data
        
        # Check if insert_one was called
        mock_db_collection.insert_one.assert_called_once()
    
    def test_create_user_as_regular_user(self, mock_db_collection):
        """Test POST /users/ as regular user (should be forbidden)."""
        # Setup - temporarily override to return regular user
        original_override = app.dependency_overrides[get_current_user]
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_REGULAR_USER)
        
        try:
            # Execute
            new_user_data = {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "role": "user"
            }
            response = client.post("/api/v1/users/", json=new_user_data)
            
            # Verify
            assert response.status_code == 403  # Forbidden
        finally:
            # Restore original override
            app.dependency_overrides[get_current_user] = original_override
    
    def test_update_own_profile(self, mock_db_collection):
        """Test PATCH /users/{user_id} for own profile."""
        # Setup - temporarily override to return regular user
        original_override = app.dependency_overrides[get_current_user]
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_REGULAR_USER)
        
        # Create an updated version of the user for the find_one after update
        updated_user = MOCK_REGULAR_USER.copy()
        updated_user["username"] = "updated_username"
        
        # Replace the find_one side_effect with a custom function
        original_find_one = mock_db_collection.find_one.side_effect
        
        def custom_find_one(query):
            """Return updated user for the regular user's ID, original behavior otherwise."""
            if "id" in query and query["id"] == MOCK_REGULAR_USER["id"]:
                return updated_user
            elif "_id" in query and query["_id"] == MOCK_REGULAR_USER["id"]:
                return updated_user
            else:
                # Use the original side_effect for other queries
                return original_find_one(query)
        
        mock_db_collection.find_one.side_effect = custom_find_one
        
        try:
            # Execute
            response = client.patch(f"/api/v1/users/{MOCK_REGULAR_USER['id']}", 
                                  json={"username": "updated_username"})
            
            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "updated_username"
            
            # Check if update_one was called
            mock_db_collection.update_one.assert_called_once()
        finally:
            # Restore original override
            app.dependency_overrides[get_current_user] = original_override
            mock_db_collection.find_one.side_effect = original_find_one
    
    def test_update_other_user_as_regular_user(self, mock_db_collection):
        """Test PATCH /users/{user_id} for another user as regular user (should be forbidden)."""
        # Setup - temporarily override to return regular user
        original_override = app.dependency_overrides[get_current_user]
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_REGULAR_USER)
        
        try:
            # Execute
            response = client.patch(f"/api/v1/users/{MOCK_ADMIN_USER['id']}", 
                                  json={"username": "hacked_admin"})
            
            # Verify
            assert response.status_code == 403  # Forbidden
        finally:
            # Restore original override
            app.dependency_overrides[get_current_user] = original_override
    
    def test_update_user_as_admin(self, mock_db_collection):
        """Test PATCH /users/{user_id} as admin."""
        # Create an updated version of the user for the find_one after update
        updated_user = MOCK_REGULAR_USER.copy()
        updated_user["email"] = "updated@example.com"
        
        # Override find_one for this specific test to return the updated user
        original_find_one = mock_db_collection.find_one.side_effect
        mock_db_collection.find_one.side_effect = lambda query: updated_user if query.get("id") == MOCK_REGULAR_USER["id"] else original_find_one(query)
        
        try:
            # Execute
            response = client.patch(f"/api/v1/users/{MOCK_REGULAR_USER['id']}", 
                                json={"email": "updated@example.com"})
            
            # Verify
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "updated@example.com"
            
            # Check if update_one was called
            mock_db_collection.update_one.assert_called_once()
        finally:
            # Restore find_one
            mock_db_collection.find_one.side_effect = original_find_one
    
    def test_delete_user_as_admin(self, mock_db_collection):
        """Test DELETE /users/{user_id} as admin."""
        # Execute
        response = client.delete(f"/api/v1/users/{MOCK_REGULAR_USER['id']}")
        
        # Verify
        assert response.status_code == 204  # No content
        
        # Check if delete_one was called
        mock_db_collection.delete_one.assert_called_once()
    
    def test_delete_user_as_regular_user(self, mock_db_collection):
        """Test DELETE /users/{user_id} as regular user (should be forbidden)."""
        # Setup - temporarily override to return regular user
        original_override = app.dependency_overrides[get_current_user]
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_REGULAR_USER)
        
        try:
            # Execute
            response = client.delete(f"/api/v1/users/{MOCK_ADMIN_USER['id']}")
            
            # Verify
            assert response.status_code == 403  # Forbidden
        finally:
            # Restore original override
            app.dependency_overrides[get_current_user] = original_override
    
    def test_filter_users(self, mock_db_collection):
        """Test GET /users/ with filters."""
        # Execute
        response = client.get("/api/v1/users/?role=admin&active=true")
        
        # Verify
        assert response.status_code == 200
        
        # Check if find was called
        mock_db_collection.find.assert_called()

    def test_invalid_username_create(self, mock_db_collection):
        """Test validation for username length."""
        # Execute - username too short
        new_user_data = {
            "username": "ab",  # Too short
            "email": "user@example.com",
            "password": "Password123!",
            "role": "user"
        }
        response = client.post("/api/v1/users/", json=new_user_data)
        
        # Verify
        assert response.status_code == 422  # Validation error
        
        # Execute - username too long
        new_user_data["username"] = "a" * 31  # Too long
        response = client.post("/api/v1/users/", json=new_user_data)
        
        # Verify
        assert response.status_code == 422  # Validation error

    def test_invalid_password_create(self, mock_db_collection):
        """Test validation for password requirements."""
        # Execute - password too short
        new_user_data = {
            "username": "validuser",
            "email": "user@example.com",
            "password": "short",
            "role": "user"
        }
        response = client.post("/api/v1/users/", json=new_user_data)
        
        # Verify
        assert response.status_code == 422  # Validation error
        
        # Execute - password missing uppercase
        new_user_data["password"] = "password123!"
        response = client.post("/api/v1/users/", json=new_user_data)
        
        # Verify
        assert response.status_code == 422  # Validation error
