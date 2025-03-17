"""
Unit tests for notification models.
"""
import uuid
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.models.notification import (
    CreateNotification,
    NotificationDB,
    NotificationResponse,
    NotificationUpdate,
    NotificationBulkUpdate
)

class TestCreateNotification:
    """Test cases for CreateNotification model."""

    def test_valid_notification(self):
        """Test valid notification creation."""
        user_id = str(uuid.uuid4())
        notification = CreateNotification(
            user_id=user_id,
            title="Device Offline",
            message="Your living room light is offline.",
            type="alert",
            priority="high",
            source="device",
            source_id=str(uuid.uuid4())
        )
        
        assert notification.user_id == user_id
        assert notification.title == "Device Offline"
        assert notification.message == "Your living room light is offline."
        assert notification.type == "alert"
        assert notification.priority == "high"
        assert notification.source == "device"
        assert notification.source_id is not None

    def test_default_values(self):
        """Test default values for optional fields."""
        user_id = str(uuid.uuid4())
        notification = CreateNotification(
            user_id=user_id,
            title="Welcome",
            message="Welcome to your smart home system!"
        )
        
        assert notification.type == "info"
        assert notification.priority == "medium"
        assert notification.source == "system"
        assert notification.source_id is None

    def test_invalid_title_too_short(self):
        """Test validation for title that's too short."""
        with pytest.raises(ValidationError) as excinfo:
            CreateNotification(
                user_id=str(uuid.uuid4()),
                title="Hi",
                message="This is a test message."
            )
        assert "Title must be at least 3 characters long" in str(excinfo.value)

    def test_invalid_title_too_long(self):
        """Test validation for title that's too long."""
        with pytest.raises(ValidationError) as excinfo:
            CreateNotification(
                user_id=str(uuid.uuid4()),
                title="A" * 101,
                message="This is a test message."
            )
        assert "Title must be less than 100 characters long" in str(excinfo.value)

    def test_invalid_message_too_short(self):
        """Test validation for message that's too short."""
        with pytest.raises(ValidationError) as excinfo:
            CreateNotification(
                user_id=str(uuid.uuid4()),
                title="Test Title",
                message="Hi"
            )
        assert "Message must be at least 5 characters long" in str(excinfo.value)

    def test_invalid_message_too_long(self):
        """Test validation for message that's too long."""
        with pytest.raises(ValidationError) as excinfo:
            CreateNotification(
                user_id=str(uuid.uuid4()),
                title="Test Title",
                message="A" * 1001
            )
        assert "Message must be less than 1000 characters long" in str(excinfo.value)

    def test_invalid_type(self):
        """Test validation for invalid notification type."""
        with pytest.raises(ValidationError) as excinfo:
            CreateNotification(
                user_id=str(uuid.uuid4()),
                title="Test Title",
                message="This is a test message.",
                type="invalid_type"
            )
        assert "type" in str(excinfo.value)

    def test_invalid_priority(self):
        """Test validation for invalid priority."""
        with pytest.raises(ValidationError) as excinfo:
            CreateNotification(
                user_id=str(uuid.uuid4()),
                title="Test Title",
                message="This is a test message.",
                priority="critical"
            )
        assert "priority" in str(excinfo.value)

    def test_invalid_source(self):
        """Test validation for invalid source."""
        with pytest.raises(ValidationError) as excinfo:
            CreateNotification(
                user_id=str(uuid.uuid4()),
                title="Test Title",
                message="This is a test message.",
                source="user"
            )
        assert "source" in str(excinfo.value)

    def test_invalid_user_id(self):
        """Test validation for invalid user_id format."""
        with pytest.raises(ValidationError) as excinfo:
            CreateNotification(
                user_id="not-a-uuid",
                title="Test Title",
                message="This is a test message."
            )
        assert "User ID must be a valid UUID" in str(excinfo.value)


class TestNotificationDB:
    """Test cases for NotificationDB model."""

    def test_notification_db_creation(self):
        """Test creating a NotificationDB instance."""
        user_id = str(uuid.uuid4())
        notification_db = NotificationDB(
            user_id=user_id,
            title="Energy Report",
            message="Your monthly energy report is available.",
            type="info",
            priority="low",
            source="system"
        )
        
        assert notification_db.id is not None
        assert notification_db.user_id == user_id
        assert notification_db.read is False
        assert notification_db.timestamp is not None
        assert notification_db.read_timestamp is None

    def test_notification_db_from_create_model(self):
        """Test creating NotificationDB from CreateNotification model."""
        user_id = str(uuid.uuid4())
        create_notification = CreateNotification(
            user_id=user_id,
            title="Motion Detected",
            message="Motion detected in your backyard.",
            type="alert",
            priority="high",
            source="device",
            source_id=str(uuid.uuid4())
        )
        
        notification_db = NotificationDB(
            **create_notification.model_dump(),
        )
        
        assert notification_db.user_id == user_id
        assert notification_db.title == "Motion Detected"
        assert notification_db.message == "Motion detected in your backyard."
        assert notification_db.type == "alert"
        assert notification_db.priority == "high"
        assert notification_db.read is False


class TestNotificationResponse:
    """Test cases for NotificationResponse model."""

    def test_notification_response_from_db(self):
        """Test creating NotificationResponse from NotificationDB."""
        user_id = str(uuid.uuid4())
        notification_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        notification_db = NotificationDB(
            id=notification_id,
            user_id=user_id,
            title="Temperature Alert",
            message="Temperature is above threshold.",
            type="alert",
            priority="high",
            source="device",
            source_id=str(uuid.uuid4()),
            read=True,
            timestamp=now,
            read_timestamp=now + timedelta(minutes=5)
        )
        
        response = NotificationResponse.model_validate(notification_db)
        
        assert response.id == notification_id
        assert response.user_id == user_id
        assert response.title == "Temperature Alert"
        assert response.message == "Temperature is above threshold."
        assert response.read is True
        assert response.timestamp == now
        assert response.read_timestamp is not None


class TestNotificationUpdate:
    """Test cases for NotificationUpdate model."""

    def test_notification_update(self):
        """Test valid notification update."""
        now = datetime.utcnow()
        update_data = NotificationUpdate(
            read=True,
            read_timestamp=now
        )
        
        assert update_data.read is True
        assert update_data.read_timestamp == now

    def test_partial_update(self):
        """Test partial update with only read status."""
        update_data = NotificationUpdate(
            read=True
        )
        
        assert update_data.read is True
        assert update_data.read_timestamp is None


class TestNotificationBulkUpdate:
    """Test cases for NotificationBulkUpdate model."""

    def test_valid_bulk_update(self):
        """Test valid bulk update."""
        notification_ids = [str(uuid.uuid4()) for _ in range(3)]
        bulk_update = NotificationBulkUpdate(
            notification_ids=notification_ids,
            read=True
        )
        
        assert bulk_update.notification_ids == notification_ids
        assert bulk_update.read is True

    def test_empty_notification_ids(self):
        """Test validation for empty notification IDs list."""
        with pytest.raises(ValidationError) as excinfo:
            NotificationBulkUpdate(
                notification_ids=[],
                read=True
            )
        assert "At least one notification ID must be provided" in str(excinfo.value)

    def test_invalid_notification_id(self):
        """Test validation for invalid notification ID in the list."""
        valid_id = str(uuid.uuid4())
        with pytest.raises(ValidationError) as excinfo:
            NotificationBulkUpdate(
                notification_ids=[valid_id, "not-a-uuid"],
                read=True
            )
        assert "Notification ID not-a-uuid must be a valid UUID" in str(excinfo.value)
