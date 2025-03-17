"""
Unit tests for analytics models.
"""
import unittest
from datetime import datetime, timedelta
import uuid

from pydantic import ValidationError
from app.models.analytics import CreateAnalytics, AnalyticsDB, AnalyticsResponse, AnalyticsUpdate, AnalyticsQuery


class TestCreateAnalytics(unittest.TestCase):
    """Test cases for CreateAnalytics model."""

    def test_valid_creation(self):
        """Test valid analytics creation."""
        valid_data = {
            "user_id": str(uuid.uuid4()),
            "device_id": str(uuid.uuid4()),
            "data_type": "energy",
            "metrics": {"value": 45.7, "unit": "kWh"},
            "tags": ["daily", "living_room"]
        }
        analytics = CreateAnalytics(**valid_data)
        self.assertEqual(analytics.user_id, valid_data["user_id"])
        self.assertEqual(analytics.device_id, valid_data["device_id"])
        self.assertEqual(analytics.data_type, valid_data["data_type"])
        self.assertEqual(analytics.metrics, valid_data["metrics"])
        self.assertEqual(analytics.tags, valid_data["tags"])

    def test_default_tags(self):
        """Test default empty tags list."""
        valid_data = {
            "user_id": str(uuid.uuid4()),
            "device_id": str(uuid.uuid4()),
            "data_type": "energy",
            "metrics": {"value": 45.7, "unit": "kWh"}
        }
        analytics = CreateAnalytics(**valid_data)
        self.assertEqual(analytics.tags, [])

    def test_invalid_user_id(self):
        """Test invalid user_id validation."""
        invalid_data = {
            "user_id": "not-a-valid-uuid",
            "device_id": str(uuid.uuid4()),
            "data_type": "energy",
            "metrics": {"value": 45.7, "unit": "kWh"}
        }
        with self.assertRaises(ValidationError):
            CreateAnalytics(**invalid_data)

    def test_invalid_device_id(self):
        """Test invalid device_id validation."""
        invalid_data = {
            "user_id": str(uuid.uuid4()),
            "device_id": "",  # Empty ID
            "data_type": "energy",
            "metrics": {"value": 45.7, "unit": "kWh"}
        }
        with self.assertRaises(ValidationError):
            CreateAnalytics(**invalid_data)

    def test_invalid_data_type(self):
        """Test invalid data_type validation."""
        invalid_data = {
            "user_id": str(uuid.uuid4()),
            "device_id": str(uuid.uuid4()),
            "data_type": "invalid_type",  # Not in valid types
            "metrics": {"value": 45.7, "unit": "kWh"}
        }
        with self.assertRaises(ValidationError):
            CreateAnalytics(**invalid_data)


class TestAnalyticsDB(unittest.TestCase):
    """Test cases for AnalyticsDB model."""

    def test_default_values(self):
        """Test default values are set correctly."""
        data = {
            "user_id": str(uuid.uuid4()),
            "device_id": str(uuid.uuid4()),
            "data_type": "temperature",
            "metrics": {"value": 22.5, "unit": "°C"}
        }
        analytics_db = AnalyticsDB(**data)
        
        # Check auto-generated fields
        self.assertIsNotNone(analytics_db.id)
        self.assertIsInstance(analytics_db.id, str)
        
        # Check timestamp set to current time (approximately)
        self.assertIsInstance(analytics_db.timestamp, datetime)
        time_diff = datetime.utcnow() - analytics_db.timestamp
        self.assertLess(time_diff.total_seconds(), 2)  # Should be less than 2 seconds
        
        # Check other defaults
        self.assertEqual(analytics_db.tags, [])
        self.assertIsNone(analytics_db.updated)


class TestAnalyticsResponse(unittest.TestCase):
    """Test cases for AnalyticsResponse model."""

    def test_response_from_db(self):
        """Test creating response from DB model."""
        db_data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "device_id": str(uuid.uuid4()),
            "data_type": "humidity",
            "metrics": {"value": 65, "unit": "%"},
            "tags": ["bathroom", "morning"],
            "timestamp": datetime.utcnow(),
            "updated": None
        }
        analytics_db = AnalyticsDB(**db_data)
        
        # Convert DB model to response model
        response = AnalyticsResponse.model_validate(analytics_db)
        
        # Check fields match
        self.assertEqual(response.id, analytics_db.id)
        self.assertEqual(response.user_id, analytics_db.user_id)
        self.assertEqual(response.device_id, analytics_db.device_id)
        self.assertEqual(response.data_type, analytics_db.data_type)
        self.assertEqual(response.metrics, analytics_db.metrics)
        self.assertEqual(response.tags, analytics_db.tags)
        self.assertEqual(response.timestamp, analytics_db.timestamp)
        
        # 'updated' field should not be in response
        with self.assertRaises(AttributeError):
            response.updated


class TestAnalyticsUpdate(unittest.TestCase):
    """Test cases for AnalyticsUpdate model."""

    def test_valid_update(self):
        """Test valid update with all fields."""
        update_data = {
            "metrics": {"value": 30.5, "unit": "°C"},
            "tags": ["bedroom", "night"]
        }
        update = AnalyticsUpdate(**update_data)
        self.assertEqual(update.metrics, update_data["metrics"])
        self.assertEqual(update.tags, update_data["tags"])

    def test_partial_update(self):
        """Test partial update with only some fields."""
        update_data = {
            "metrics": {"value": 30.5, "unit": "°C"}
        }
        update = AnalyticsUpdate(**update_data)
        self.assertEqual(update.metrics, update_data["metrics"])
        self.assertIsNone(update.tags)

    def test_invalid_tags(self):
        """Test validation of tags field."""
        update_data = {
            "tags": ["valid", ""]  # Empty tag
        }
        with self.assertRaises(ValidationError):
            AnalyticsUpdate(**update_data)


class TestAnalyticsQuery(unittest.TestCase):
    """Test cases for AnalyticsQuery model."""

    def test_valid_query(self):
        """Test valid query with all fields."""
        now = datetime.utcnow()
        query_data = {
            "user_id": str(uuid.uuid4()),
            "device_id": str(uuid.uuid4()),
            "data_type": "energy",
            "start_time": now - timedelta(days=7),
            "end_time": now,
            "tags": ["kitchen", "appliance"]
        }
        query = AnalyticsQuery(**query_data)
        
        # Validate all fields match
        for key, value in query_data.items():
            self.assertEqual(getattr(query, key), value)

    def test_empty_query(self):
        """Test empty query (all fields None)."""
        query = AnalyticsQuery()
        self.assertIsNone(query.user_id)
        self.assertIsNone(query.device_id)
        self.assertIsNone(query.data_type)
        self.assertIsNone(query.start_time)
        self.assertIsNone(query.end_time)
        self.assertIsNone(query.tags)

    def test_time_range_validation(self):
        """Test validation of time range."""
        now = datetime.utcnow()
        
        # Valid time range
        valid_query = AnalyticsQuery(
            start_time=now - timedelta(days=7),
            end_time=now
        )
        valid_query.validate_time_range_post_init()  # Should not raise
        
        # Invalid time range
        invalid_query = AnalyticsQuery(
            start_time=now,
            end_time=now - timedelta(days=7)
        )
        with self.assertRaises(ValueError):
            invalid_query.validate_time_range_post_init()


if __name__ == "__main__":
    unittest.main()
