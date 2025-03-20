"""
Tests for analytics routes.
"""
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import uuid

# Import the app
sys.path.append(".")
from app.main import app
from app.models.user import UserDB
from app.models.analytics import AnalyticsDB

# Initialize test client
client = TestClient(app)

# Mock user data
MOCK_ADMIN = {
    "id": str(uuid.uuid4()),  # Using valid UUID format
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
    "id": str(uuid.uuid4()),  # Using valid UUID format
    "username": "testuser",
    "email": "user@example.com",
    "hashed_password": "hashed_password",
    "active": True,
    "verified": True,
    "created": datetime.utcnow(),
    "updated": None,
    "role": "user"
}

# Mock analytics data
def create_mock_analytics(user_id, device_id=None, data_type="energy"):
    now = datetime.utcnow()
    return {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "device_id": device_id or str(uuid.uuid4()),
        "data_type": data_type,
        "metrics": {"value": 100.5, "unit": "kWh"},
        "tags": ["monthly", "summary"],
        "timestamp": now,
        "updated": None
    }

MOCK_ADMIN_ANALYTICS = create_mock_analytics(MOCK_ADMIN["id"])
MOCK_USER_ANALYTICS = create_mock_analytics(MOCK_USER["id"])

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


# Override auth dependency for tests
from app.core.auth import get_current_user

# Default to admin for most tests
app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)


class TestAnalyticsRoutes:
    
    @patch("app.routes.analytics_routes.an_c")
    def test_get_all_analytics(self, mock_collection):
        """Test getting all analytics."""
        # Setup the mock to return our test analytics
        mock_cursor = MockCursor([MOCK_ADMIN_ANALYTICS, MOCK_USER_ANALYTICS])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        response = client.get("/api/v1/analytics/")
        
        # Verify response
        assert response.status_code == 200
        analytics = response.json()
        assert len(analytics) == 2
        
        # Verify the mock was called
        mock_collection.find.assert_called_once()
    
    @patch("app.routes.analytics_routes.an_c")
    def test_get_analytics_by_id(self, mock_collection):
        """Test getting analytics by ID."""
        # Setup the mock
        mock_collection.find_one.return_value = MOCK_USER_ANALYTICS
        
        # Call the endpoint
        response = client.get(f"/api/v1/analytics/{MOCK_USER_ANALYTICS['id']}")
        
        # Verify response
        assert response.status_code == 200
        analytics = response.json()
        assert analytics["id"] == MOCK_USER_ANALYTICS["id"]
        
        # Verify the mock was called with correct parameters
        mock_collection.find_one.assert_called_once_with({"id": MOCK_USER_ANALYTICS["id"]})
    
    @patch("app.routes.analytics_routes.an_c")
    def test_get_analytics_not_found(self, mock_collection):
        """Test getting a non-existent analytics record."""
        # Setup the mock
        mock_collection.find_one.return_value = None
        
        # Call the endpoint
        response = client.get("/api/v1/analytics/nonexistent-id")
        
        # Verify response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    @patch("app.routes.analytics_routes.an_c")
    @patch("app.models.analytics.CreateAnalytics.validate_id")
    @patch("app.models.analytics.CreateAnalytics.validate_data_type")
    def test_create_analytics(self, mock_type_validator, mock_id_validator, mock_collection):
        """Test creating analytics."""
        # Setup the mock
        mock_collection.insert_one.return_value = MagicMock()
        
        # Setup validators to pass validation and return the input value
        mock_id_validator.side_effect = lambda cls, v: v
        mock_type_validator.side_effect = lambda cls, v: v
        
        # Call the endpoint
        device_id = str(uuid.uuid4())
        new_analytics_data = {
            "user_id": MOCK_USER["id"],
            "device_id": device_id,
            "data_type": "energy",
            "metrics": {"value": 150.0, "unit": "kWh"},
            "tags": ["daily"]
        }
        
        response = client.post("/api/v1/analytics/", json=new_analytics_data)
        
        # For debugging if the test fails
        if response.status_code != 201:
            print(f"Response error: {response.text}")
            
        # Verify response
        assert response.status_code == 201, f"Failed with response: {response.text}"
        analytics = response.json()
        assert analytics["user_id"] == MOCK_USER["id"]
        assert analytics["metrics"]["value"] == 150.0
        
        # Verify the mock was called
        assert mock_collection.insert_one.call_count == 1
    
    @patch("app.routes.analytics_routes.an_c")
    def test_update_analytics(self, mock_collection):
        """Test updating analytics."""
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_USER_ANALYTICS
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        # Updated analytics after update
        updated_analytics = MOCK_USER_ANALYTICS.copy()
        updated_analytics["metrics"] = {"value": 200.0, "unit": "kWh"}
        updated_analytics["updated"] = datetime.utcnow()
        
        # Setup mock to return updated analytics on second call
        mock_collection.find_one.side_effect = [MOCK_USER_ANALYTICS, updated_analytics]
        
        # Call the endpoint
        update_data = {
            "metrics": {"value": 200.0, "unit": "kWh"}
        }
        response = client.patch(f"/api/v1/analytics/{MOCK_USER_ANALYTICS['id']}", json=update_data)
        
        # Verify response
        assert response.status_code == 200
        analytics = response.json()
        assert analytics["metrics"]["value"] == 200.0
        
        # Verify the mock was called with correct parameters
        mock_collection.find_one.assert_called_with({"id": MOCK_USER_ANALYTICS["id"]})
        mock_collection.update_one.assert_called_once()
    
    @patch("app.routes.analytics_routes.an_c")
    def test_delete_analytics(self, mock_collection):
        """Test deleting analytics."""
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_USER_ANALYTICS
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Call the endpoint
        response = client.delete(f"/api/v1/analytics/{MOCK_USER_ANALYTICS['id']}")
        
        # Verify response
        assert response.status_code == 204
        
        # Verify the mock was called with correct parameters
        mock_collection.find_one.assert_called_with({"id": MOCK_USER_ANALYTICS["id"]})
        mock_collection.delete_one.assert_called_once_with({"id": MOCK_USER_ANALYTICS["id"]})
    
    @patch("app.routes.analytics_routes.an_c")
    def test_user_access_restriction(self, mock_collection):
        """Test that regular users can only access their own analytics."""
        # Override the auth dependency to return a regular user
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        # Setup the mock to return admin's analytics
        mock_collection.find_one.return_value = MOCK_ADMIN_ANALYTICS
        
        # Call the endpoint - should be forbidden
        response = client.get(f"/api/v1/analytics/{MOCK_ADMIN_ANALYTICS['id']}")
        
        # Verify response shows forbidden
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
        
        # Reset the auth override
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_ADMIN)
    
    @patch("app.routes.analytics_routes.an_c")
    def test_analytics_filtering(self, mock_collection):
        """Test filtering analytics by various parameters."""
        # Setup the mock
        mock_cursor = MockCursor([MOCK_USER_ANALYTICS])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint with filters
        response = client.get(
            "/api/v1/analytics/",
            params={
                "user_id": MOCK_USER["id"],
                "data_type": "energy",
                "tags": ["monthly"]
            }
        )
        
        # Verify response
        assert response.status_code == 200
        
        # Verify the mock was called with correct filtering
        mock_collection.find.assert_called_once()
        args, _ = mock_collection.find.call_args
        query = args[0]
        assert query["user_id"] == MOCK_USER["id"]
        assert query["data_type"] == "energy"
        assert "tags" in query and "$in" in query["tags"]
        assert "monthly" in query["tags"]["$in"]
    
    @patch("app.routes.analytics_routes.an_c")
    def test_time_range_filtering(self, mock_collection):
        """Test filtering analytics by time range."""
        # Setup the mock
        mock_cursor = MockCursor([MOCK_USER_ANALYTICS])
        mock_collection.find.return_value = mock_cursor
        
        # Prepare time parameters
        end_time = datetime.utcnow().isoformat()
        start_time = (datetime.utcnow() - timedelta(days=7)).isoformat()
        
        # Call the endpoint with time range filters
        response = client.get(
            "/api/v1/analytics/",
            params={
                "start_time": start_time,
                "end_time": end_time
            }
        )
        
        # Verify response
        assert response.status_code == 200
        
        # Verify the mock was called with correct time filtering
        mock_collection.find.assert_called_once()
        args, _ = mock_collection.find.call_args
        query = args[0]
        assert "timestamp" in query
        assert "$gte" in query["timestamp"]
        assert "$lte" in query["timestamp"]
