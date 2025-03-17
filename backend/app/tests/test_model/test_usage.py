"""
Unit tests for Usage models.
"""
import uuid
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.models.usage import (
    CreateUsage,
    UsageDB,
    UsageResponse,
    UsageUpdate,
    UsageAggregateResponse,
    UsageBulkCreate,
    UsageTimeRange,
)


class TestCreateUsage:
    """Tests for the CreateUsage model."""

    def test_valid_create_usage(self):
        """Test that valid data passes validation."""
        data = {
            "device_id": str(uuid.uuid4()),
            "metrics": {"temperature": 22.5, "humidity": 45},
            "duration": 300,
            "energy_consumed": 0.5,
            "status": "active"
        }
        usage = CreateUsage(**data)
        assert usage.device_id == data["device_id"]
        assert usage.metrics == data["metrics"]
        assert usage.duration == data["duration"]
        assert usage.energy_consumed == data["energy_consumed"]
        assert usage.status == data["status"]
        assert usage.timestamp is None  # Default value

    def test_minimal_create_usage(self):
        """Test that only required fields are sufficient."""
        data = {
            "device_id": str(uuid.uuid4()),
            "metrics": {"power": 100}
        }
        usage = CreateUsage(**data)
        assert usage.device_id == data["device_id"]
        assert usage.metrics == data["metrics"]
        assert usage.timestamp is None
        assert usage.duration is None
        assert usage.energy_consumed is None
        assert usage.status is None

    def test_invalid_device_id(self):
        """Test that invalid device_id fails validation."""
        data = {
            "device_id": "",  # Empty string
            "metrics": {"temperature": 22.5}
        }
        with pytest.raises(ValidationError):
            CreateUsage(**data)
        
        data["device_id"] = None  # None value
        with pytest.raises(ValidationError):
            CreateUsage(**data)

    def test_negative_energy_consumed(self):
        """Test that negative energy_consumed fails validation."""
        data = {
            "device_id": str(uuid.uuid4()),
            "metrics": {"temperature": 22.5},
            "energy_consumed": -1.5
        }
        with pytest.raises(ValidationError):
            CreateUsage(**data)

    def test_negative_duration(self):
        """Test that negative duration fails validation."""
        data = {
            "device_id": str(uuid.uuid4()),
            "metrics": {"temperature": 22.5},
            "duration": -300
        }
        with pytest.raises(ValidationError):
            CreateUsage(**data)


class TestUsageDB:
    """Tests for the UsageDB model."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        data = {
            "device_id": str(uuid.uuid4()),
            "metrics": {"temperature": 22.5}
        }
        usage_db = UsageDB(**data)
        assert isinstance(usage_db.id, str)
        assert len(usage_db.id) > 0
        assert isinstance(usage_db.timestamp, datetime)
        assert isinstance(usage_db.created, datetime)
        assert usage_db.updated is None
        
    def test_custom_values(self):
        """Test that custom values override defaults."""
        custom_id = str(uuid.uuid4())
        custom_timestamp = datetime.utcnow() - timedelta(hours=1)
        custom_created = datetime.utcnow() - timedelta(days=1)
        
        data = {
            "id": custom_id,
            "device_id": str(uuid.uuid4()),
            "metrics": {"temperature": 22.5},
            "timestamp": custom_timestamp,
            "created": custom_created,
            "updated": datetime.utcnow()
        }
        usage_db = UsageDB(**data)
        assert usage_db.id == custom_id
        assert usage_db.timestamp == custom_timestamp
        assert usage_db.created == custom_created
        assert usage_db.updated is not None


class TestUsageResponse:
    """Tests for the UsageResponse model."""

    def test_response_model(self):
        """Test UsageResponse model creation from UsageDB."""
        usage_db = UsageDB(
            id=str(uuid.uuid4()),
            device_id=str(uuid.uuid4()),
            metrics={"temperature": 22.5, "humidity": 45},
            timestamp=datetime.utcnow(),
            duration=300,
            energy_consumed=0.5,
            status="active",
            created=datetime.utcnow(),
            updated=None
        )
        
        # Convert to dict and create UsageResponse
        usage_response = UsageResponse.model_validate(usage_db)
        
        # Check that fields match
        assert usage_response.id == usage_db.id
        assert usage_response.device_id == usage_db.device_id
        assert usage_response.metrics == usage_db.metrics
        assert usage_response.timestamp == usage_db.timestamp
        assert usage_response.duration == usage_db.duration
        assert usage_response.energy_consumed == usage_db.energy_consumed
        assert usage_response.status == usage_db.status
        
        # Check that internal fields are not included
        with pytest.raises(AttributeError):
            usage_response.created
        with pytest.raises(AttributeError):
            usage_response.updated


class TestUsageUpdate:
    """Tests for the UsageUpdate model."""

    def test_valid_update(self):
        """Test valid partial update."""
        data = {
            "metrics": {"temperature": 23.5},
            "duration": 350,
            "status": "idle"
        }
        update = UsageUpdate(**data)
        assert update.metrics == data["metrics"]
        assert update.duration == data["duration"]
        assert update.status == data["status"]
        assert update.energy_consumed is None

    def test_empty_update(self):
        """Test that empty update is valid."""
        update = UsageUpdate()
        assert update.metrics is None
        assert update.duration is None
        assert update.energy_consumed is None
        assert update.status is None

    def test_negative_values_update(self):
        """Test that negative values fail validation in updates."""
        data = {"energy_consumed": -0.5}
        with pytest.raises(ValidationError):
            UsageUpdate(**data)
        
        data = {"duration": -100}
        with pytest.raises(ValidationError):
            UsageUpdate(**data)


class TestUsageAggregateResponse:
    """Tests for the UsageAggregateResponse model."""

    def test_aggregate_response(self):
        """Test the aggregate response model."""
        data = {
            "device_id": str(uuid.uuid4()),
            "start_date": datetime.utcnow() - timedelta(days=7),
            "end_date": datetime.utcnow(),
            "total_duration": 3600,
            "total_energy": 2.5,
            "average_metrics": {"temperature": 22.5, "humidity": 45},
            "usage_count": 24
        }
        response = UsageAggregateResponse(**data)
        assert response.device_id == data["device_id"]
        assert response.start_date == data["start_date"]
        assert response.end_date == data["end_date"]
        assert response.total_duration == data["total_duration"]
        assert response.total_energy == data["total_energy"]
        assert response.average_metrics == data["average_metrics"]
        assert response.usage_count == data["usage_count"]

    def test_default_values(self):
        """Test default values in aggregate response."""
        data = {
            "device_id": str(uuid.uuid4()),
            "start_date": datetime.utcnow() - timedelta(days=7),
            "end_date": datetime.utcnow(),
        }
        response = UsageAggregateResponse(**data)
        assert response.total_duration == 0
        assert response.total_energy == 0
        assert response.average_metrics == {}
        assert response.usage_count == 0


class TestUsageBulkCreate:
    """Tests for the UsageBulkCreate model."""

    def test_valid_bulk_create(self):
        """Test valid bulk creation."""
        records = [
            CreateUsage(
                device_id=str(uuid.uuid4()),
                metrics={"temperature": 22.5}
            ),
            CreateUsage(
                device_id=str(uuid.uuid4()),
                metrics={"humidity": 45},
                duration=300
            )
        ]
        bulk_create = UsageBulkCreate(records=records)
        assert len(bulk_create.records) == 2
        assert bulk_create.records[0].metrics["temperature"] == 22.5
        assert bulk_create.records[1].duration == 300

    def test_empty_records_list(self):
        """Test that empty records list fails validation."""
        with pytest.raises(ValidationError):
            UsageBulkCreate(records=[])


class TestUsageTimeRange:
    """Tests for the UsageTimeRange model."""

    def test_valid_time_range(self):
        """Test valid time range."""
        start = datetime.utcnow() - timedelta(days=7)
        end = datetime.utcnow()
        device_id = str(uuid.uuid4())
        
        time_range = UsageTimeRange(
            start_time=start,
            end_time=end,
            device_id=device_id
        )
        assert time_range.start_time == start
        assert time_range.end_time == end
        assert time_range.device_id == device_id

    def test_invalid_time_range(self):
        """Test that end time before start time fails validation."""
        start = datetime.utcnow()
        end = datetime.utcnow() - timedelta(days=1)  # End before start
        
        with pytest.raises(ValidationError):
            UsageTimeRange(
                start_time=start,
                end_time=end
            )

    def test_optional_device_id(self):
        """Test that device_id is optional."""
        start = datetime.utcnow() - timedelta(days=7)
        end = datetime.utcnow()
        
        time_range = UsageTimeRange(
            start_time=start,
            end_time=end
        )
        assert time_range.start_time == start
        assert time_range.end_time == end
        assert time_range.device_id is None
