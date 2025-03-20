"""
Test file for energy goal routes.
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
from app.models.goal import GoalType, GoalStatus, GoalTimeframe

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

# Mock goal data
MOCK_GOAL_1 = {
    "id": "goal-id-123",
    "user_id": "user-id-456",
    "title": "Reduce Energy Usage",
    "description": "Reduce household energy usage by 10% this month",
    "type": "energy_saving",
    "target_value": 100.0,
    "current_value": 25.0,
    "progress_percentage": 25.0,
    "timeframe": "monthly",
    "start_date": datetime.utcnow(),
    "end_date": None,
    "status": "active",
    "related_devices": ["device-id-1", "device-id-2"],
    "created": datetime.utcnow(),
    "updated": None
}

MOCK_GOAL_2 = {
    "id": "goal-id-456",
    "user_id": "admin-id-123",
    "title": "Peak Time Avoidance",
    "description": "Avoid using major appliances during peak hours",
    "type": "peak_avoidance",
    "target_value": 50.0,
    "current_value": 10.0,
    "progress_percentage": 20.0,
    "timeframe": "weekly",
    "start_date": datetime.utcnow(),
    "end_date": None,
    "status": "active",
    "related_devices": ["device-id-3"],
    "created": datetime.utcnow(),
    "updated": None
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


class TestGoalRoutes:
    
    @patch("app.routes.goal_routes.g_c")
    def test_get_all_goals(self, mock_collection):
        """Test getting all goals."""
        # Setup the mock to return our test goals
        mock_cursor = MockCursor([MOCK_GOAL_1, MOCK_GOAL_2])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint
        response = client.get("/api/v1/goals/")
        
        # Verify response
        assert response.status_code == 200
        goals = response.json()
        assert len(goals) == 2
        assert goals[0]["id"] == MOCK_GOAL_1["id"]
        assert goals[1]["id"] == MOCK_GOAL_2["id"]
        
        # Verify the mock was called
        mock_collection.find.assert_called_once()
    
    @patch("app.routes.goal_routes.g_c")
    def test_get_goal_by_id(self, mock_collection):
        """Test getting a goal by ID."""
        # Setup the mock
        mock_collection.find_one.return_value = MOCK_GOAL_1
        
        # Call the endpoint
        response = client.get(f"/api/v1/goals/{MOCK_GOAL_1['id']}")
        
        # Verify response
        assert response.status_code == 200
        goal = response.json()
        assert goal["id"] == MOCK_GOAL_1["id"]
        
        # Verify the mock was called with correct parameters
        mock_collection.find_one.assert_called_once_with({"id": MOCK_GOAL_1["id"]})
    
    @patch("app.routes.goal_routes.g_c")
    def test_create_goal(self, mock_collection):
        """Test creating a goal."""
        # Setup the mocks
        mock_collection.insert_one.return_value = MagicMock()
        
        # Call the endpoint
        new_goal_data = {
            "user_id": "admin-id-123",
            "title": "New Energy Goal",
            "description": "A description that is long enough to pass validation",
            "type": "consumption_limit",
            "target_value": 200.0,
            "timeframe": "daily",
            "start_date": datetime.utcnow().isoformat(),
            "related_devices": ["device-id-4"]
        }
        response = client.post("/api/v1/goals/", json=new_goal_data)
        
        # Verify response
        assert response.status_code == 201
        goal = response.json()
        assert goal["title"] == "New Energy Goal"
        
        # Verify mock calls
        assert mock_collection.insert_one.call_count == 1
    
    @patch("app.routes.goal_routes.g_c")
    def test_update_goal(self, mock_collection):
        """Test updating a goal."""
        # Setup the mocks
        updated_goal = MOCK_GOAL_1.copy()
        updated_goal["title"] = "Updated Goal Title"
        
        mock_collection.find_one.side_effect = [MOCK_GOAL_1, updated_goal]
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        # Call the endpoint
        update_data = {
            "title": "Updated Goal Title"
        }
        response = client.patch(f"/api/v1/goals/{MOCK_GOAL_1['id']}", json=update_data)
        
        # Verify response
        assert response.status_code == 200
        goal = response.json()
        assert goal["title"] == "Updated Goal Title"
        
        # Verify mock calls
        assert mock_collection.find_one.call_count == 2
        assert mock_collection.update_one.call_count == 1
    
    @patch("app.routes.goal_routes.g_c")
    def test_update_goal_progress(self, mock_collection):
        """Test updating a goal's progress."""
        # Setup the mocks
        updated_goal = MOCK_GOAL_1.copy()
        updated_goal["current_value"] = 50.0
        updated_goal["progress_percentage"] = 50.0
        
        mock_collection.find_one.side_effect = [MOCK_GOAL_1, updated_goal]
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        # Call the endpoint
        progress_data = {
            "current_value": 50.0
        }
        response = client.patch(f"/api/v1/goals/{MOCK_GOAL_1['id']}/progress", json=progress_data)
        
        # Verify response
        assert response.status_code == 200
        goal = response.json()
        assert goal["current_value"] == 50.0
        assert goal["progress_percentage"] == 50.0
        
        # Verify mock calls
        assert mock_collection.find_one.call_count == 2
        assert mock_collection.update_one.call_count == 1
    
    @patch("app.routes.goal_routes.g_c")
    def test_delete_goal(self, mock_collection):
        """Test deleting a goal."""
        # Setup the mocks
        mock_collection.find_one.return_value = MOCK_GOAL_1
        mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Call the endpoint
        response = client.delete(f"/api/v1/goals/{MOCK_GOAL_1['id']}")
        
        # Verify response
        assert response.status_code == 204
        
        # Verify mock calls
        assert mock_collection.find_one.call_count == 1
        mock_collection.delete_one.assert_called_once_with({"id": MOCK_GOAL_1["id"]})
    
    @patch("app.routes.goal_routes.g_c")
    def test_get_goals_with_filters(self, mock_collection):
        """Test getting goals with filters."""
        # Setup the mock
        mock_cursor = MockCursor([MOCK_GOAL_1])
        mock_collection.find.return_value = mock_cursor
        
        # Call the endpoint with filters
        response = client.get("/api/v1/goals/?type=energy_saving&status=active")
        
        # Verify response
        assert response.status_code == 200
        goals = response.json()
        assert len(goals) == 1
        assert goals[0]["id"] == MOCK_GOAL_1["id"]
        
        # Verify the mock was called with correct filter parameters
        mock_collection.find.assert_called_once()
    
    @patch("app.routes.goal_routes.g_c")
    def test_goal_not_found(self, mock_collection):
        """Test error when goal not found."""
        # Setup the mock
        mock_collection.find_one.return_value = None
        
        # Call the endpoint
        response = client.get("/api/v1/goals/nonexistent-id")
        
        # Verify response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
        
    @patch("app.routes.goal_routes.g_c")
    def test_unauthorized_access(self, mock_collection):
        """Test error when unauthorized user tries to access a goal."""
        # Override auth dependency for this test
        original_override = app.dependency_overrides[get_current_user]
        app.dependency_overrides[get_current_user] = lambda: UserDB(**MOCK_USER)
        
        try:
            # Setup the mock - a goal owned by admin
            mock_collection.find_one.return_value = MOCK_GOAL_2
            
            # Call the endpoint
            response = client.get(f"/api/v1/goals/{MOCK_GOAL_2['id']}")
            
            # Verify response
            assert response.status_code == 403
            assert "Not authorized" in response.json()["detail"]
        finally:
            # Restore original auth override
            app.dependency_overrides[get_current_user] = original_override
    
    @patch("app.routes.goal_routes.g_c")
    def test_complete_goal_automatically(self, mock_collection):
        """Test goal is automatically marked as completed when target is reached."""
        # Setup the mocks
        goal = MOCK_GOAL_1.copy()
        goal["current_value"] = 50.0
        goal["progress_percentage"] = 50.0
        
        updated_goal = goal.copy()
        updated_goal["current_value"] = 100.0
        updated_goal["progress_percentage"] = 100.0
        updated_goal["status"] = "completed"
        
        mock_collection.find_one.side_effect = [goal, updated_goal]
        mock_collection.update_one.return_value = MagicMock(modified_count=1)
        
        # Call the endpoint
        progress_data = {
            "current_value": 100.0
        }
        response = client.patch(f"/api/v1/goals/{goal['id']}/progress", json=progress_data)
        
        # Verify response
        assert response.status_code == 200
        updated = response.json()
        assert updated["current_value"] == 100.0
        assert updated["progress_percentage"] == 100.0
        assert updated["status"] == "completed"
