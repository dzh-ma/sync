"""
Tests for profile management routes.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.models.profile import ProfileDB, ProfileResponse
from app.models.user import UserDB
from app.core.auth import get_current_user
from app.routes.profile_routes import router as profile_router

# Mock data
mock_admin_user = UserDB(
    id="admin123",
    username="admin",
    email="admin@example.com",
    hashed_password="hashed_password",
    role="admin",
    active=True,
    created=datetime.now(timezone.utc)
)

mock_regular_user = UserDB(
    id="user123",
    username="user",
    email="user@example.com",
    hashed_password="hashed_password",
    role="user",
    active=True,
    created=datetime.now(timezone.utc)
)

mock_profile = ProfileDB(
    id="profile123",
    user_id="user123",
    first_name="John",
    last_name="Doe",
    timezone="UTC",
    temperature_unit="C",
    dark_mode=False,
    favorite_devices=[],
    created=datetime.now(timezone.utc)
)

mock_admin_profile = ProfileDB(
    id="profile456",
    user_id="admin123",
    first_name="Admin",
    last_name="User",
    timezone="UTC",
    temperature_unit="F",
    dark_mode=True,
    favorite_devices=["device123"],
    created=datetime.now(timezone.utc)
)

# Create test client function with dependency override
def get_test_client(mock_user):
    """Create a test client with the specified user for auth"""
    app = FastAPI()
    
    # Create a dependency override for authentication
    async def mock_get_current_user():
        return mock_user
        
    app.include_router(profile_router)
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    return TestClient(app)

# Tests
def test_get_all_profiles_admin():
    # Setup - get client with admin user
    client = get_test_client(mock_admin_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock
        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [mock_profile.model_dump(), mock_admin_profile.model_dump()]
        mock_p_c.find.return_value = mock_cursor
        
        # Execute
        response = client.get("/profiles/")
        
        # Assert
        assert response.status_code == 200
        profiles = response.json()
        assert len(profiles) == 2
        assert profiles[0]["id"] == mock_profile.id
        assert profiles[1]["id"] == mock_admin_profile.id
        
        # Verify admin can see all profiles
        mock_p_c.find.assert_called_once()
        # Empty query means all profiles
        assert mock_p_c.find.call_args[0][0] == {}


def test_get_all_profiles_regular_user():
    # Setup - get client with regular user
    client = get_test_client(mock_regular_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock
        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [mock_profile.model_dump()]
        mock_p_c.find.return_value = mock_cursor
        
        # Execute
        response = client.get("/profiles/")
        
        # Assert
        assert response.status_code == 200
        profiles = response.json()
        assert len(profiles) == 1
        assert profiles[0]["id"] == mock_profile.id
        
        # Verify regular user can only see their own profile
        mock_p_c.find.assert_called_once()
        # Query should include user_id filter
        assert mock_p_c.find.call_args[0][0]["user_id"] == "user123"


def test_get_all_profiles_with_filters():
    # Setup
    client = get_test_client(mock_admin_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock
        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [mock_admin_profile.model_dump()]
        mock_p_c.find.return_value = mock_cursor
        
        # Execute - with filters
        response = client.get("/profiles/?temperature_unit=F&dark_mode=true")
        
        # Assert
        assert response.status_code == 200
        profiles = response.json()
        assert len(profiles) == 1
        assert profiles[0]["id"] == mock_admin_profile.id
        
        # Verify filters were applied
        mock_p_c.find.assert_called_once()
        assert mock_p_c.find.call_args[0][0] == {
            "temperature_unit": "F", 
            "dark_mode": True
        }


def test_get_profile_by_id_admin():
    # Setup
    client = get_test_client(mock_admin_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock
        mock_p_c.find_one.return_value = mock_profile.model_dump()
        
        # Execute
        response = client.get(f"/profiles/{mock_profile.id}")
        
        # Assert
        assert response.status_code == 200
        profile = response.json()
        assert profile["id"] == mock_profile.id
        assert profile["user_id"] == mock_profile.user_id
        
        # Verify query
        mock_p_c.find_one.assert_called_once_with({"id": mock_profile.id})


def test_get_profile_by_id_regular_user_own_profile():
    # Setup
    client = get_test_client(mock_regular_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock
        mock_p_c.find_one.return_value = mock_profile.model_dump()
        
        # Execute
        response = client.get(f"/profiles/{mock_profile.id}")
        
        # Assert
        assert response.status_code == 200
        profile = response.json()
        assert profile["id"] == mock_profile.id
        assert profile["user_id"] == mock_regular_user.id  # Own profile


def test_get_profile_by_id_regular_user_other_profile():
    # Setup
    client = get_test_client(mock_regular_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock - trying to access admin profile
        mock_p_c.find_one.return_value = mock_admin_profile.model_dump()
        
        # Execute
        response = client.get(f"/profiles/{mock_admin_profile.id}")
        
        # Assert
        assert response.status_code == 403  # Forbidden
        assert "Not authorized" in response.json()["detail"]


def test_get_profile_not_found():
    # Setup
    client = get_test_client(mock_admin_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock - no profile found
        mock_p_c.find_one.return_value = None
        
        # Execute
        response = client.get("/profiles/nonexistent")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


def test_create_profile_admin():
    # Setup
    client = get_test_client(mock_admin_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock - no existing profile
        mock_p_c.find_one.return_value = None
        mock_p_c.insert_one.return_value = MagicMock()
        
        # Execute
        profile_data = {
            "user_id": "new_user",
            "first_name": "New",
            "last_name": "User",
            "timezone": "UTC",
            "temperature_unit": "C",
            "dark_mode": False
        }
        response = client.post("/profiles/", json=profile_data)
        
        # Assert
        assert response.status_code == 201
        created_profile = response.json()
        assert created_profile["user_id"] == "new_user"
        assert created_profile["first_name"] == "New"
        
        # Verify database operations
        mock_p_c.find_one.assert_called_once_with({"user_id": "new_user"})
        mock_p_c.insert_one.assert_called_once()


def test_create_profile_regular_user_own_profile():
    # Setup
    client = get_test_client(mock_regular_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock - no existing profile
        mock_p_c.find_one.return_value = None
        mock_p_c.insert_one.return_value = MagicMock()
        
        # Execute - creating own profile
        profile_data = {
            "user_id": mock_regular_user.id,  # Own user ID
            "first_name": "John",
            "last_name": "Doe",
            "timezone": "UTC",
            "temperature_unit": "C",
            "dark_mode": False
        }
        response = client.post("/profiles/", json=profile_data)
        
        # Assert
        assert response.status_code == 201
        created_profile = response.json()
        assert created_profile["user_id"] == mock_regular_user.id
        
        # Verify database operations
        mock_p_c.find_one.assert_called_once_with({"user_id": mock_regular_user.id})
        mock_p_c.insert_one.assert_called_once()


def test_create_profile_regular_user_other_profile():
    # Setup
    client = get_test_client(mock_regular_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock
        mock_p_c.find_one.return_value = None
        
        # Execute - trying to create profile for someone else
        profile_data = {
            "user_id": "other_user",  # Different user ID
            "first_name": "Other",
            "last_name": "User",
            "timezone": "UTC",
            "temperature_unit": "C",
            "dark_mode": False
        }
        response = client.post("/profiles/", json=profile_data)
        
        # Assert
        assert response.status_code == 403  # Forbidden
        assert "Not authorized" in response.json()["detail"]
        
        # Verify no database insertion
        mock_p_c.insert_one.assert_not_called()


def test_create_profile_duplicate():
    # Setup
    client = get_test_client(mock_admin_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock - existing profile found
        mock_p_c.find_one.return_value = mock_profile.model_dump()
        
        # Execute
        profile_data = {
            "user_id": mock_profile.user_id,  # Already exists
            "first_name": "New",
            "last_name": "User",
            "timezone": "UTC",
            "temperature_unit": "C",
            "dark_mode": False
        }
        response = client.post("/profiles/", json=profile_data)
        
        # Assert
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
        
        # Verify no insertion attempt
        mock_p_c.insert_one.assert_not_called()


def test_update_profile_admin():
    # Setup
    client = get_test_client(mock_admin_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock
        updated_profile = mock_profile.model_dump()
        updated_profile["first_name"] = "Updated"
        mock_p_c.find_one.side_effect = [
            mock_profile.model_dump(),  # First call: find profile
            updated_profile  # Second call: after update
        ]
        mock_p_c.update_one.return_value = MagicMock(modified_count=1)
        
        # Execute
        update_data = {
            "first_name": "Updated",
            "temperature_unit": "F"
        }
        response = client.patch(f"/profiles/{mock_profile.id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        updated_profile_response = response.json()
        assert updated_profile_response["first_name"] == "Updated"
        
        # Verify update operation
        mock_p_c.update_one.assert_called_once()
        # Check that updated timestamp was added
        update_args = mock_p_c.update_one.call_args[0]
        assert "updated" in update_args[1]["$set"]
        assert "first_name" in update_args[1]["$set"]
        assert "temperature_unit" in update_args[1]["$set"]


def test_update_profile_regular_user_own_profile():
    # Setup
    client = get_test_client(mock_regular_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock
        updated_profile = mock_profile.model_dump()
        updated_profile["dark_mode"] = True
        mock_p_c.find_one.side_effect = [
            mock_profile.model_dump(),  # First call: find profile
            updated_profile  # Second call: after update
        ]
        mock_p_c.update_one.return_value = MagicMock(modified_count=1)
        
        # Execute - update own profile
        update_data = {"dark_mode": True}
        response = client.patch(f"/profiles/{mock_profile.id}", json=update_data)
        
        # Assert
        assert response.status_code == 200
        updated_profile_response = response.json()
        assert updated_profile_response["dark_mode"] is True
        
        # Verify update operation
        mock_p_c.update_one.assert_called_once()


def test_update_profile_regular_user_other_profile():
    # Setup
    client = get_test_client(mock_regular_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock - trying to update admin's profile
        mock_p_c.find_one.return_value = mock_admin_profile.model_dump()
        
        # Execute
        update_data = {"first_name": "Hacked"}
        response = client.patch(f"/profiles/{mock_admin_profile.id}", json=update_data)
        
        # Assert
        assert response.status_code == 403  # Forbidden
        assert "Not authorized" in response.json()["detail"]
        
        # Verify no update attempt
        mock_p_c.update_one.assert_not_called()


def test_update_profile_not_found():
    # Setup
    client = get_test_client(mock_admin_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock - profile not found
        mock_p_c.find_one.return_value = None
        
        # Execute
        update_data = {"first_name": "Updated"}
        response = client.patch("/profiles/nonexistent", json=update_data)
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        
        # Verify no update attempt
        mock_p_c.update_one.assert_not_called()


def test_delete_profile_admin():
    # Setup
    client = get_test_client(mock_admin_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock
        mock_p_c.find_one.return_value = mock_profile.model_dump()
        mock_p_c.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Execute
        response = client.delete(f"/profiles/{mock_profile.id}")
        
        # Assert
        assert response.status_code == 204
        assert response.content == b''  # No content
        
        # Verify deletion
        mock_p_c.delete_one.assert_called_once_with({"id": mock_profile.id})


def test_delete_profile_regular_user_own_profile():
    # Setup
    client = get_test_client(mock_regular_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock - own profile
        mock_p_c.find_one.return_value = mock_profile.model_dump()
        mock_p_c.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Execute
        response = client.delete(f"/profiles/{mock_profile.id}")
        
        # Assert
        assert response.status_code == 204
        assert response.content == b''  # No content
        
        # Verify deletion
        mock_p_c.delete_one.assert_called_once_with({"id": mock_profile.id})


def test_delete_profile_regular_user_other_profile():
    # Setup
    client = get_test_client(mock_regular_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock - admin's profile
        mock_p_c.find_one.return_value = mock_admin_profile.model_dump()
        
        # Execute
        response = client.delete(f"/profiles/{mock_admin_profile.id}")
        
        # Assert
        assert response.status_code == 403  # Forbidden
        assert "Not authorized" in response.json()["detail"]
        
        # Verify no deletion attempt
        mock_p_c.delete_one.assert_not_called()


def test_delete_profile_not_found():
    # Setup
    client = get_test_client(mock_admin_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock - profile not found
        mock_p_c.find_one.return_value = None
        
        # Execute
        response = client.delete("/profiles/nonexistent")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        
        # Verify no deletion attempt
        mock_p_c.delete_one.assert_not_called()


def test_pagination():
    # Setup
    client = get_test_client(mock_admin_user)
    
    with patch("app.routes.profile_routes.p_c") as mock_p_c:
        # Configure mock
        mock_cursor = MagicMock()
        mock_cursor.skip.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.__iter__.return_value = [mock_profile.model_dump()]
        mock_p_c.find.return_value = mock_cursor
        
        # Execute with pagination
        response = client.get("/profiles/?skip=10&limit=5")
        
        # Assert
        assert response.status_code == 200
        
        # Verify pagination parameters were passed
        mock_cursor.skip.assert_called_once_with(10)
        mock_cursor.limit.assert_called_once_with(5)
