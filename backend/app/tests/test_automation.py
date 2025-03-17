"""
Unit tests for automation models.
"""
import unittest
from datetime import datetime, timedelta
import pytest
from pydantic import ValidationError

from app.models.automation import (
    CreateAutomation,
    AutomationDB,
    AutomationResponse,
    AutomationDetailResponse,
    AutomationUpdate,
    TriggerType,
    ActionType
)


class TestAutomationModels(unittest.TestCase):
    """Test suite for automation models."""

    def setUp(self):
        """Set up test data."""
        self.valid_automation_data = {
            "name": "Evening Lights",
            "description": "Turn on living room lights at sunset",
            "user_id": "user123",
            "device_id": "device456",
            "enabled": True,
            "trigger_type": TriggerType.TIME,
            "trigger_data": {"time": "19:00:00", "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]},
            "action_type": ActionType.DEVICE_CONTROL,
            "action_data": {"command": "turn_on", "brightness": 80}
        }
        
        self.valid_automation_data_with_conditions = {
            **self.valid_automation_data,
            "conditions": [
                {"type": "presence", "value": "home"},
                {"type": "light_level", "operator": "<", "value": 100}
            ]
        }

    def test_create_automation_valid(self):
        """Test creating a valid automation."""
        automation = CreateAutomation(**self.valid_automation_data)
        self.assertEqual(automation.name, "Evening Lights")
        self.assertEqual(automation.trigger_type, TriggerType.TIME)
        self.assertEqual(automation.action_type, ActionType.DEVICE_CONTROL)

    def test_create_automation_with_conditions(self):
        """Test creating a valid automation with conditions."""
        automation = CreateAutomation(**self.valid_automation_data_with_conditions)
        self.assertEqual(len(automation.conditions), 2)
        self.assertEqual(automation.conditions[0]["type"], "presence")

    def test_create_automation_name_too_short(self):
        """Test validation for short name."""
        invalid_data = self.valid_automation_data.copy()
        invalid_data["name"] = "ab"  # too short
        
        with pytest.raises(ValidationError) as excinfo:
            CreateAutomation(**invalid_data)
        
        self.assertIn("Automation name must be at least 3 characters long", str(excinfo.value))

    def test_create_automation_name_too_long(self):
        """Test validation for long name."""
        invalid_data = self.valid_automation_data.copy()
        invalid_data["name"] = "a" * 51  # too long
        
        with pytest.raises(ValidationError) as excinfo:
            CreateAutomation(**invalid_data)
        
        self.assertIn("Automation name must be less than 50 characters long", str(excinfo.value))

    def test_create_automation_description_too_long(self):
        """Test validation for long description."""
        invalid_data = self.valid_automation_data.copy()
        invalid_data["description"] = "a" * 501  # too long
        
        with pytest.raises(ValidationError) as excinfo:
            CreateAutomation(**invalid_data)
        
        self.assertIn("Automation description must be less than 500 characters long", str(excinfo.value))

    def test_automation_db_model(self):
        """Test AutomationDB model."""
        # Create basic automation
        automation_db = AutomationDB(**self.valid_automation_data)
        
        # Check auto-generated fields
        self.assertIsNotNone(automation_db.id)
        self.assertIsInstance(automation_db.created, datetime)
        self.assertIsNone(automation_db.updated)
        self.assertIsNone(automation_db.last_triggered)
        self.assertEqual(automation_db.execution_count, 0)

    def test_automation_response_model(self):
        """Test AutomationResponse model."""
        # Create DB model first
        automation_db = AutomationDB(**self.valid_automation_data)
        
        # Convert to response model
        response = AutomationResponse.model_validate(automation_db)
        
        # Check that response has expected fields
        self.assertEqual(response.id, automation_db.id)
        self.assertEqual(response.name, automation_db.name)
        self.assertEqual(response.user_id, automation_db.user_id)
        self.assertEqual(response.device_id, automation_db.device_id)
        
        # Check that response does NOT include detailed data
        with pytest.raises(AttributeError):
            _ = response.trigger_data
        with pytest.raises(AttributeError):
            _ = response.action_data

    def test_automation_detail_response_model(self):
        """Test AutomationDetailResponse model."""
        # Create DB model first
        automation_db = AutomationDB(**self.valid_automation_data_with_conditions)
        
        # Convert to detail response model
        detail_response = AutomationDetailResponse.model_validate(automation_db)
        
        # Check that detail response has all fields including configuration data
        self.assertEqual(detail_response.id, automation_db.id)
        self.assertEqual(detail_response.trigger_data, automation_db.trigger_data)
        self.assertEqual(detail_response.action_data, automation_db.action_data)
        self.assertEqual(detail_response.conditions, automation_db.conditions)

    def test_automation_update_valid(self):
        """Test valid automation update."""
        update_data = {
            "name": "Updated Lights",
            "enabled": False
        }
        
        update = AutomationUpdate(**update_data)
        self.assertEqual(update.name, "Updated Lights")
        self.assertEqual(update.enabled, False)
        self.assertIsNone(update.description)  # Not included in update

    def test_automation_update_validation(self):
        """Test validation in automation update."""
        update_data = {
            "name": "ab"  # too short
        }
        
        with pytest.raises(ValidationError) as excinfo:
            AutomationUpdate(**update_data)
        
        self.assertIn("Automation name must be at least 3 characters long", str(excinfo.value))

    def test_update_with_enum_values(self):
        """Test update with enum values."""
        update_data = {
            "trigger_type": TriggerType.SENSOR,
            "action_type": ActionType.NOTIFICATION,
            "trigger_data": {"sensor_id": "temp001", "threshold": 25, "operator": ">"},
            "action_data": {"message": "Temperature too high", "severity": "warning"}
        }
        
        update = AutomationUpdate(**update_data)
        self.assertEqual(update.trigger_type, TriggerType.SENSOR)
        self.assertEqual(update.action_type, ActionType.NOTIFICATION)
        self.assertEqual(update.trigger_data["threshold"], 25)

    def test_full_update_flow(self):
        """Test a complete update flow from creation to update."""
        # Create initial automation in DB
        automation_db = AutomationDB(**self.valid_automation_data)
        
        # Create an update
        update_data = {
            "name": "Updated Lights",
            "enabled": False,
            "trigger_data": {"time": "20:00:00", "days": ["fri", "sat", "sun"]}
        }
        update = AutomationUpdate(**update_data)
        
        # Apply update to DB model
        now = datetime.utcnow()
        
        # In a real application, you'd update the fields one by one or use a utility function
        if update.name is not None:
            automation_db.name = update.name
        if update.enabled is not None:
            automation_db.enabled = update.enabled
        if update.trigger_data is not None:
            automation_db.trigger_data = update.trigger_data
        automation_db.updated = now
        
        # Verify updates applied correctly
        self.assertEqual(automation_db.name, "Updated Lights")
        self.assertEqual(automation_db.enabled, False)
        self.assertEqual(automation_db.trigger_data["time"], "20:00:00")
        self.assertEqual(automation_db.updated, now)
        
        # Original fields still intact
        self.assertEqual(automation_db.description, "Turn on living room lights at sunset")
        self.assertEqual(automation_db.user_id, "user123")


if __name__ == "__main__":
    unittest.main()
