"""
Unit tests for the Energy Goal models.
"""
import unittest
from datetime import datetime, timedelta
import uuid
import pytest
from pydantic import ValidationError

from app.models.goal import (
    CreateEnergyGoal,
    EnergyGoalDB,
    EnergyGoalResponse,
    EnergyGoalUpdate,
    EnergyGoalProgressUpdate,
    GoalType,
    GoalStatus,
    GoalTimeframe
)


class TestEnergyGoalModels(unittest.TestCase):
    """Test cases for energy goal models."""

    def setUp(self):
        """Set up test data."""
        self.user_id = str(uuid.uuid4())
        self.now = datetime.utcnow()
        self.future = self.now + timedelta(days=30)
        self.valid_goal_data = {
            "user_id": self.user_id,
            "title": "Reduce electricity usage",
            "description": "Reduce overall electricity consumption by 20% during summer months",
            "type": GoalType.ENERGY_SAVING,
            "target_value": 200.5,
            "timeframe": GoalTimeframe.MONTHLY,
            "start_date": self.now,
            "end_date": self.future,
            "related_devices": [str(uuid.uuid4()), str(uuid.uuid4())]
        }

    def test_create_energy_goal_valid(self):
        """Test creating a valid energy goal."""
        goal = CreateEnergyGoal(**self.valid_goal_data)
        self.assertEqual(goal.user_id, self.valid_goal_data["user_id"])
        self.assertEqual(goal.title, self.valid_goal_data["title"])
        self.assertEqual(goal.target_value, self.valid_goal_data["target_value"])
        self.assertEqual(goal.timeframe, self.valid_goal_data["timeframe"])

    def test_create_energy_goal_title_too_short(self):
        """Test validation error when title is too short."""
        invalid_data = self.valid_goal_data.copy()
        invalid_data["title"] = "Ab"
        with pytest.raises(ValidationError) as excinfo:
            CreateEnergyGoal(**invalid_data)
        assert "Title must be at least 3 characters long" in str(excinfo.value)

    def test_create_energy_goal_description_too_short(self):
        """Test validation error when description is too short."""
        invalid_data = self.valid_goal_data.copy()
        invalid_data["description"] = "Too short"
        with pytest.raises(ValidationError) as excinfo:
            CreateEnergyGoal(**invalid_data)
        assert "Description must be at least 10 characters long" in str(excinfo.value)

    def test_create_energy_goal_negative_target(self):
        """Test validation error when target value is negative."""
        invalid_data = self.valid_goal_data.copy()
        invalid_data["target_value"] = -10.5
        with pytest.raises(ValidationError) as excinfo:
            CreateEnergyGoal(**invalid_data)
        assert "Target value must be greater than 0" in str(excinfo.value)

    def test_create_energy_goal_custom_timeframe_no_end_date(self):
        """Test validation error when custom timeframe has no end date."""
        invalid_data = self.valid_goal_data.copy()
        invalid_data["timeframe"] = GoalTimeframe.CUSTOM
        invalid_data["end_date"] = None
        with pytest.raises(ValidationError) as excinfo:
            CreateEnergyGoal(**invalid_data)
        assert "End date is required for custom timeframe" in str(excinfo.value)

    def test_create_energy_goal_end_date_before_start(self):
        """Test validation error when end date is before start date."""
        invalid_data = self.valid_goal_data.copy()
        invalid_data["end_date"] = self.now - timedelta(days=1)
        with pytest.raises(ValidationError) as excinfo:
            CreateEnergyGoal(**invalid_data)
        assert "End date must be after start date" in str(excinfo.value)

    def test_energy_goal_db_model(self):
        """Test the database model for energy goal."""
        # First create with minimum required fields
        goal_db = EnergyGoalDB(
            user_id=self.user_id,
            title="Reduce electricity usage",
            description="Reduce overall electricity consumption by 20% during summer months",
            type=GoalType.ENERGY_SAVING,
            target_value=200.5,
            timeframe=GoalTimeframe.MONTHLY,
            start_date=self.now
        )
        
        # Validate defaults
        self.assertIsNotNone(goal_db.id)
        self.assertEqual(goal_db.current_value, 0.0)
        self.assertEqual(goal_db.progress_percentage, 0.0)
        self.assertEqual(goal_db.status, GoalStatus.ACTIVE)
        self.assertEqual(goal_db.related_devices, [])
        self.assertIsNotNone(goal_db.created)
        self.assertIsNone(goal_db.updated)

    def test_energy_goal_response_model(self):
        """Test the response model for energy goal."""
        goal_id = str(uuid.uuid4())
        response_data = {
            "id": goal_id,
            "user_id": self.user_id,
            "title": "Reduce electricity usage",
            "description": "Reduce overall electricity consumption by 20% during summer months",
            "type": "energy_saving",
            "target_value": 200.5,
            "current_value": 50.25,
            "progress_percentage": 25.0,
            "timeframe": "monthly",
            "start_date": self.now,
            "end_date": self.future,
            "status": "active",
            "related_devices": [str(uuid.uuid4())],
            "created": self.now
        }
        
        response = EnergyGoalResponse(**response_data)
        self.assertEqual(response.id, goal_id)
        self.assertEqual(response.user_id, self.user_id)
        self.assertEqual(response.progress_percentage, 25.0)

    def test_energy_goal_update_model(self):
        """Test the update model for energy goal."""
        update_data = {
            "title": "Updated goal title",
            "target_value": 300.0,
            "status": GoalStatus.PAUSED,
        }
        
        update = EnergyGoalUpdate(**update_data)
        self.assertEqual(update.title, "Updated goal title")
        self.assertEqual(update.target_value, 300.0)
        self.assertEqual(update.status, GoalStatus.PAUSED)
        self.assertIsNone(update.description)
        self.assertIsNone(update.current_value)

    def test_energy_goal_update_validation(self):
        """Test validation in the update model."""
        invalid_update = {
            "title": "A",  # Too short
            "target_value": -50.0  # Negative
        }
        
        with pytest.raises(ValidationError) as excinfo:
            EnergyGoalUpdate(**invalid_update)
        
        error_str = str(excinfo.value)
        assert "Title must be at least 3 characters long" in error_str
        assert "Target value must be greater than 0" in error_str

    def test_energy_goal_progress_update(self):
        """Test the progress update model."""
        # Valid update
        update = EnergyGoalProgressUpdate(current_value=75.5)
        self.assertEqual(update.current_value, 75.5)
        
        # Invalid negative value
        with pytest.raises(ValidationError) as excinfo:
            EnergyGoalProgressUpdate(current_value=-10.0)
        assert "Current value cannot be negative" in str(excinfo.value)


if __name__ == "__main__":
    unittest.main()
