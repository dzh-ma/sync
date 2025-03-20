"""
Test file for usage routes.
"""
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta, timezone

# Import the app
sys.path.append(".")
from app.main import app
from app.models.user import UserDB
from app.models.usage import UsageDB

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

# Mock device data
MOCK_DEVICE_1 = {
    "id": "device-id-123",
    "user_id": "user-id-456",  # Owned by MOCK_USER
    "name": "Living Room Smart Thermostat",
    "type": "thermostat",
    "active": True
}

MOCK_DEVICE_2 = {
    "id": "device-id-456",
    "user_id": "user-id-789",  # Owned by another user
    "name": "Bedroom Smart Light",
    "type": "light",
    "active": True
}

# Mock usage data
current_time = datetime.now(timezone.utc)

MOCK_USAGE_1 = {
    "id": "usage-id-123",
    "device_id": "device-id-123",
    "metrics": {"temperature": 22.5, "humidity": 50},
    "timestamp": current_time - timedelta(hours=1),
    "duration": 3600,
    "energy_consumed": 1.5,
    "status": "active",
    "created": current_time - timedelta(hours=1),
    "updated": None
}

MOCK_USAGE_2 = {
    "id": "usage-id-456",
    "device_id": "device-id-456",
    "metrics": {"temperature": 23.0, "humidity": 48},
    "timestamp": current_time,
    "duration": 1800,
    "energy_consumed": 0.8,
    "status": "standby",
    "created": current_time,
    "updated": None
}

# Override auth dependency - default to admin
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
    
    def sort(self, field, direction):
        return self
    
    def __iter__(self):
        return iter(self.items)


class TestUsageRoutes:
    
    def setup_method(self):
        # Reset the auth dependency to admin for each test
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
    
    @patch("app.routes.usage_routes.us_c")
    def test_get_all_usage_admin(self, mock_usage_collection):
        """Test getting all usage records as admin."""
        # Setup the mock to return our test usage records
        mock_cursor = MockCursor([MOCK_USAGE_1, MOCK_USAGE_2])
        mock_usage_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        response = client.get("/api/v1/usage/")
        
        # Verify response
        assert response.status_code == 200
        usage_records = response.json()
        assert len(usage_records) == 2
        assert usage_records[0]["id"] == MOCK_USAGE_1["id"]
        assert usage_records[1]["id"] == MOCK_USAGE_2["id"]
        
        # Verify the mock was called
        mock_usage_collection.find.assert_called_once()
    
    @patch("app.routes.usage_routes.us_c")
    @patch("app.routes.usage_routes.d_c")
    def test_get_all_usage_user(self, mock_device_collection, mock_usage_collection):
        """Test getting all usage records as regular user."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock for device collection to return user's devices
        mock_device_collection.find.return_value = [MOCK_DEVICE_1]
        
        # Setup the mock for usage collection
        mock_cursor = MockCursor([MOCK_USAGE_1])
        mock_usage_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        response = client.get("/api/v1/usage/")
        
        # Verify response
        assert response.status_code == 200
        usage_records = response.json()
        assert len(usage_records) == 1
        assert usage_records[0]["id"] == MOCK_USAGE_1["id"]
        
        # Verify the device collection was queried for user's devices
        mock_device_collection.find.assert_called_once_with({"user_id": MOCK_USER["id"]})
    
    @patch("app.routes.usage_routes.us_c")
    def test_get_usage_by_id_admin(self, mock_collection):
        """Test getting a usage record by ID as admin."""
        # Setup the mock
        mock_collection.find_one.return_value = MOCK_USAGE_1
        
        # Call the endpoint
        response = client.get(f"/api/v1/usage/{MOCK_USAGE_1['id']}")
        
        # Verify response
        assert response.status_code == 200
        usage = response.json()
        assert usage["id"] == MOCK_USAGE_1["id"]
        
        # Verify the mock was called with correct parameters
        mock_collection.find_one.assert_called_once_with({"id": MOCK_USAGE_1["id"]})
    
    @patch("app.routes.usage_routes.us_c")
    @patch("app.routes.usage_routes.check_device_ownership")
    def test_get_usage_by_id_user_owned(self, mock_check_ownership, mock_collection):
        """Test getting a usage record by ID as regular user (device owned by user)."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_USAGE_1
        mock_check_ownership.return_value = True  # User owns the device
        
        # Call the endpoint
        response = client.get(f"/api/v1/usage/{MOCK_USAGE_1['id']}")
        
        # Verify response
        assert response.status_code == 200
        usage = response.json()
        assert usage["id"] == MOCK_USAGE_1["id"]
    
    @patch("app.routes.usage_routes.us_c")
    @patch("app.routes.usage_routes.check_device_ownership")
    def test_get_usage_by_id_user_not_owned(self, mock_check_ownership, mock_collection):
        """Test getting a usage record by ID as regular user (device not owned by user)."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_USAGE_2
        mock_check_ownership.return_value = False  # User doesn't own the device
        
        # Call the endpoint
        response = client.get(f"/api/v1/usage/{MOCK_USAGE_2['id']}")
        
        # Verify response (should be forbidden)
        assert response.status_code == 403
    
    @patch("app.routes.usage_routes.us_c")
    def test_create_usage_admin(self, mock_collection):
        """Test creating a usage record as admin."""
        # Setup the mocks
        mock_collection.insert_one.return_value = MagicMock()
        
        # Call the endpoint
        new_usage_data = {
            "device_id": "device-id-123",
            "metrics": {"temperature": 22.5, "humidity": 50},
            "duration": 3600,
            "energy_consumed": 1.5,
            "status": "active"
        }
        response = client.post("/api/v1/usage/", json=new_usage_data)
        
        # Verify response
        assert response.status_code == 201
        usage = response.json()
        assert usage["device_id"] == "device-id-123"
        
        # Verify mock calls
        assert mock_collection.insert_one.call_count == 1
    
    @patch("app.routes.usage_routes.us_c")
    @patch("app.routes.usage_routes.check_device_ownership")
    def test_create_usage_user_owned(self, mock_check_ownership, mock_collection):
        """Test creating a usage record as regular user (device owned by user)."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mocks
        mock_collection.insert_one.return_value = MagicMock()
        mock_check_ownership.return_value = True  # User owns the device
        
        # Call the endpoint
        new_usage_data = {
            "device_id": "device-id-123",
            "metrics": {"temperature": 22.5, "humidity": 50},
            "duration": 3600,
            "energy_consumed": 1.5,
            "status": "active"
        }
        response = client.post("/api/v1/usage/", json=new_usage_data)
        
        # Verify response
        assert response.status_code == 201
        usage = response.json()
        assert usage["device_id"] == "device-id-123"
    
    @patch("app.routes.usage_routes.us_c")
    @patch("app.routes.usage_routes.check_device_ownership")
    def test_create_usage_user_not_owned(self, mock_check_ownership, mock_collection):
        """Test creating a usage record as regular user (device not owned by user)."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mocks
        mock_collection.insert_one.return_value = MagicMock()
        mock_check_ownership.return_value = False  # User doesn't own the device
        
        # Call the endpoint
        new_usage_data = {
            "device_id": "device-id-456",  # Not owned by user
            "metrics": {"temperature": 23.0, "humidity": 48},
            "duration": 1800,
            "energy_consumed": 0.8,
            "status": "standby"
        }
        response = client.post("/api/v1/usage/", json=new_usage_data)
        
        # Verify response (should be forbidden)
        assert response.status_code == 403
    
    @patch("app.routes.usage_routes.us_c")
    def test_update_usage_admin(self, mock_collection):
        """Test updating a usage record as admin."""
        # Setup the mocks
        mock_collection.find_one.side_effect = [MOCK_USAGE_1, {**MOCK_USAGE_1, "status": "inactive"}]
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        # Call the endpoint
        update_data = {"status": "inactive"}
        response = client.patch(f"/api/v1/usage/{MOCK_USAGE_1['id']}", json=update_data)
        
        # Verify response
        assert response.status_code == 200
        usage = response.json()
        assert usage["status"] == "inactive"
        
        # Verify mock calls
        mock_collection.find_one.assert_called_with({"id": MOCK_USAGE_1["id"]})
        mock_collection.update_one.assert_called_once()
    
    @patch("app.routes.usage_routes.us_c")
    @patch("app.routes.usage_routes.check_device_ownership")
    def test_update_usage_user_owned(self, mock_check_ownership, mock_collection):
        """Test updating a usage record as regular user (device owned by user)."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mocks
        mock_collection.find_one.side_effect = [MOCK_USAGE_1, {**MOCK_USAGE_1, "status": "inactive"}]
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        mock_check_ownership.return_value = True  # User owns the device
        
        # Call the endpoint
        update_data = {"status": "inactive"}
        response = client.patch(f"/api/v1/usage/{MOCK_USAGE_1['id']}", json=update_data)
        
        # Verify response
        assert response.status_code == 200
        usage = response.json()
        assert usage["status"] == "inactive"
    
    @patch("app.routes.usage_routes.us_c")
    @patch("app.routes.usage_routes.check_device_ownership")
    def test_update_usage_user_not_owned(self, mock_check_ownership, mock_collection):
        """Test updating a usage record as regular user (device not owned by user)."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_USAGE_2
        mock_check_ownership.return_value = False  # User doesn't own the device
        
        # Call the endpoint
        update_data = {"status": "inactive"}
        response = client.patch(f"/api/v1/usage/{MOCK_USAGE_2['id']}", json=update_data)
        
        # Verify response (should be forbidden)
        assert response.status_code == 403
    
    @patch("app.routes.usage_routes.us_c")
    def test_delete_usage_admin(self, mock_collection):
        """Test deleting a usage record as admin."""
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_USAGE_1
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Call the endpoint
        response = client.delete(f"/api/v1/usage/{MOCK_USAGE_1['id']}")
        
        # Verify response
        assert response.status_code == 204
        
        # Verify mock calls
        mock_collection.find_one.assert_called_once_with({"id": MOCK_USAGE_1["id"]})
        mock_collection.delete_one.assert_called_once_with({"id": MOCK_USAGE_1["id"]})
    
    @patch("app.routes.usage_routes.us_c")
    @patch("app.routes.usage_routes.check_device_ownership")
    def test_delete_usage_user_owned(self, mock_check_ownership, mock_collection):
        """Test deleting a usage record as regular user (device owned by user)."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_USAGE_1
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        mock_check_ownership.return_value = True  # User owns the device
        
        # Call the endpoint
        response = client.delete(f"/api/v1/usage/{MOCK_USAGE_1['id']}")
        
        # Verify response
        assert response.status_code == 204
    
    @patch("app.routes.usage_routes.us_c")
    @patch("app.routes.usage_routes.check_device_ownership")
    def test_delete_usage_user_not_owned(self, mock_check_ownership, mock_collection):
        """Test deleting a usage record as regular user (device not owned by user)."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_USAGE_2
        mock_check_ownership.return_value = False  # User doesn't own the device
        
        # Call the endpoint
        response = client.delete(f"/api/v1/usage/{MOCK_USAGE_2['id']}")
        
        # Verify response (should be forbidden)
        assert response.status_code == 403
    
    @patch("app.routes.usage_routes.us_c")
    def test_bulk_create_usage_admin(self, mock_collection):
        """Test bulk creating usage records as admin."""
        # Setup the mocks
        mock_collection.insert_one.return_value = MagicMock()
        
        # Call the endpoint
        bulk_data = {
            "records": [
                {
                    "device_id": "device-id-123",
                    "metrics": {"temperature": 22.5, "humidity": 50},
                    "duration": 3600,
                    "energy_consumed": 1.5,
                    "status": "active"
                },
                {
                    "device_id": "device-id-456",
                    "metrics": {"temperature": 23.0, "humidity": 48},
                    "duration": 1800,
                    "energy_consumed": 0.8,
                    "status": "standby"
                }
            ]
        }
        response = client.post("/api/v1/usage/bulk", json=bulk_data)
        
        # Verify response
        assert response.status_code == 201
        usage_records = response.json()
        assert len(usage_records) == 2
        
        # Verify mock calls
        assert mock_collection.insert_one.call_count == 2
    
    @patch("app.routes.usage_routes.us_c")
    @patch("app.routes.usage_routes.check_device_ownership")
    def test_bulk_create_usage_user(self, mock_check_ownership, mock_collection):
        """Test bulk creating usage records as regular user."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mocks
        mock_collection.insert_one.return_value = MagicMock()
        
        # First device is owned, second is not
        mock_check_ownership.side_effect = [True, False]
        
        # Call the endpoint
        bulk_data = {
            "records": [
                {
                    "device_id": "device-id-123",  # Owned by user
                    "metrics": {"temperature": 22.5, "humidity": 50},
                    "duration": 3600,
                    "energy_consumed": 1.5,
                    "status": "active"
                },
                {
                    "device_id": "device-id-456",  # Not owned by user
                    "metrics": {"temperature": 23.0, "humidity": 48},
                    "duration": 1800,
                    "energy_consumed": 0.8,
                    "status": "standby"
                }
            ]
        }
        response = client.post("/api/v1/usage/bulk", json=bulk_data)
        
        # Verify response (should be forbidden because of second device)
        assert response.status_code == 403
    
    @patch("app.routes.usage_routes.us_c")
    def test_get_usage_aggregate_admin(self, mock_collection):
        """Test getting aggregated usage statistics as admin."""
        # Setup the mocks
        mock_cursor = MockCursor([MOCK_USAGE_1, MOCK_USAGE_2])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        start_time = current_time - timedelta(hours=2)
        end_time = current_time
        payload = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "device_id": "device-id-123"
        }
        response = client.post("/api/v1/usage/aggregate/", json=payload)
        
        # Verify response
        assert response.status_code == 200
        usage_aggregate = response.json()
        assert usage_aggregate["device_id"] == "device-id-123"
        assert "total_duration" in usage_aggregate
        assert "total_energy" in usage_aggregate
        
        # Verify mock calls
        mock_collection.find.assert_called_once()
    
    @patch("app.routes.usage_routes.us_c")
    @patch("app.routes.usage_routes.check_device_ownership")
    def test_get_usage_aggregate_user_owned(self, mock_check_ownership, mock_collection):
        """Test getting aggregated usage statistics as regular user (device owned by user)."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mocks
        mock_cursor = MockCursor([MOCK_USAGE_1])
        mock_collection.find.return_value = mock_cursor
        mock_check_ownership.return_value = True  # User owns the device
        
        # Call the endpoint
        start_time = current_time - timedelta(hours=2)
        end_time = current_time
        payload = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "device_id": "device-id-123"
        }
        response = client.post("/api/v1/usage/aggregate/", json=payload)
        
        # Verify response
        assert response.status_code == 200
        usage_aggregate = response.json()
        assert usage_aggregate["device_id"] == "device-id-123"
    
    @patch("app.routes.usage_routes.check_device_ownership")
    def test_get_usage_aggregate_user_not_owned(self, mock_check_ownership):
        """Test getting aggregated usage statistics as regular user (device not owned by user)."""
        # Set auth to regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock
        mock_check_ownership.return_value = False  # User doesn't own the device
        
        # Call the endpoint
        start_time = current_time - timedelta(hours=2)
        end_time = current_time
        payload = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "device_id": "device-id-456"
        }
        response = client.post("/api/v1/usage/aggregate/", json=payload)
        
        # Verify response (should be forbidden)
        assert response.status_code == 403

    @patch("app.routes.usage_routes.us_c")
    def test_get_usage_not_found(self, mock_collection):
        """Test getting a non-existent usage record."""
        # Setup the mock
        mock_collection.find_one.return_value = None
        
        # Call the endpoint
        response = client.get("/api/v1/usage/nonexistent-id")
        
        # Verify response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @patch("app.routes.usage_routes.us_c")
    def test_update_usage_validation_error(self, mock_collection):
        """Test updating a usage record with invalid data."""
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_USAGE_1
        
        # Call the endpoint with negative energy consumption
        update_data = {"energy_consumed": -5.0}
        response = client.patch(f"/api/v1/usage/{MOCK_USAGE_1['id']}", json=update_data)
        
        # Verify response
        assert response.status_code == 422  # Validation error
