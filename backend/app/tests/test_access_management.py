"""
Unit tests for access management models.
"""
import uuid
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.models.access_management import (
    ResourceType,
    AccessLevel,
    CreateAccessManagement,
    AccessManagementDB,
    AccessManagementResponse,
    AccessManagementUpdate
)


class TestCreateAccessManagement:
    """Test cases for CreateAccessManagement model."""

    def test_valid_creation(self):
        """Test creating a valid access management entry."""
        data = {
            "owner_id": str(uuid.uuid4()),
            "resource_id": str(uuid.uuid4()),
            "resource_type": ResourceType.DEVICE,
            "user_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
            "access_level": AccessLevel.READ,
            "expires_at": datetime.utcnow() + timedelta(days=30),
            "note": "Sharing living room lights"
        }
        
        access = CreateAccessManagement(**data)
        assert access.owner_id == data["owner_id"]
        assert access.resource_id == data["resource_id"]
        assert access.resource_type == ResourceType.DEVICE
        assert len(access.user_ids) == 2
        assert access.access_level == AccessLevel.READ
        assert access.note == "Sharing living room lights"

    def test_minimal_creation(self):
        """Test creating with minimal required fields."""
        data = {
            "owner_id": str(uuid.uuid4()),
            "resource_id": str(uuid.uuid4()),
            "resource_type": ResourceType.ROOM,
            "user_ids": [str(uuid.uuid4())],
            "access_level": AccessLevel.CONTROL
        }
        
        access = CreateAccessManagement(**data)
        assert access.expires_at is None
        assert access.note is None

    def test_empty_user_ids(self):
        """Test validation error when user_ids is empty."""
        data = {
            "owner_id": str(uuid.uuid4()),
            "resource_id": str(uuid.uuid4()),
            "resource_type": ResourceType.DEVICE,
            "user_ids": [],
            "access_level": AccessLevel.READ
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CreateAccessManagement(**data)
        
        assert "At least one user ID must be provided" in str(exc_info.value)

    def test_too_many_user_ids(self):
        """Test validation error when too many user_ids are provided."""
        data = {
            "owner_id": str(uuid.uuid4()),
            "resource_id": str(uuid.uuid4()),
            "resource_type": ResourceType.DEVICE,
            "user_ids": [str(uuid.uuid4()) for _ in range(51)],
            "access_level": AccessLevel.READ
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CreateAccessManagement(**data)
        
        assert "Cannot share with more than 50 users" in str(exc_info.value)

    def test_note_too_long(self):
        """Test validation error when note is too long."""
        data = {
            "owner_id": str(uuid.uuid4()),
            "resource_id": str(uuid.uuid4()),
            "resource_type": ResourceType.DEVICE,
            "user_ids": [str(uuid.uuid4())],
            "access_level": AccessLevel.READ,
            "note": "x" * 201  # 201 characters
        }
        
        with pytest.raises(ValidationError) as exc_info:
            CreateAccessManagement(**data)
        
        assert "Note must be less than 200 characters" in str(exc_info.value)


class TestAccessManagementDB:
    """Test cases for AccessManagementDB model."""

    def test_default_values(self):
        """Test default values are set correctly."""
        owner_id = str(uuid.uuid4())
        resource_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        access_db = AccessManagementDB(
            owner_id=owner_id,
            resource_id=resource_id,
            resource_type=ResourceType.HOME,
            user_id=user_id,
            access_level=AccessLevel.ADMIN
        )
        
        assert isinstance(access_db.id, str)
        assert len(access_db.id) > 0
        assert access_db.owner_id == owner_id
        assert access_db.resource_id == resource_id
        assert access_db.user_id == user_id
        assert access_db.resource_type == ResourceType.HOME
        assert access_db.access_level == AccessLevel.ADMIN
        assert isinstance(access_db.created, datetime)
        assert access_db.updated is None
        assert access_db.expires_at is None
        assert access_db.active is True
        assert access_db.note is None


class TestAccessManagementResponse:
    """Test cases for AccessManagementResponse model."""

    def test_model_serialization(self):
        """Test model serialization works correctly."""
        data = {
            "id": str(uuid.uuid4()),
            "owner_id": str(uuid.uuid4()),
            "resource_id": str(uuid.uuid4()),
            "resource_type": ResourceType.DEVICE,
            "user_id": str(uuid.uuid4()),
            "access_level": AccessLevel.CONTROL,
            "created": datetime.utcnow(),
            "active": True
        }
        
        response = AccessManagementResponse(**data)
        serialized = response.model_dump()
        
        assert serialized["id"] == data["id"]
        assert serialized["owner_id"] == data["owner_id"]
        assert serialized["resource_id"] == data["resource_id"]
        assert serialized["resource_type"] == ResourceType.DEVICE
        assert serialized["user_id"] == data["user_id"]
        assert serialized["access_level"] == AccessLevel.CONTROL
        assert serialized["active"] is True
        assert "expires_at" in serialized


class TestAccessManagementUpdate:
    """Test cases for AccessManagementUpdate model."""

    def test_partial_update(self):
        """Test partial update with some fields."""
        update_data = {
            "access_level": AccessLevel.MANAGE,
            "active": False
        }
        
        update = AccessManagementUpdate(**update_data)
        assert update.access_level == AccessLevel.MANAGE
        assert update.active is False
        assert update.expires_at is None
        assert update.note is None

    def test_note_validation(self):
        """Test note validation in update model."""
        update_data = {
            "note": "x" * 201  # 201 characters
        }
        
        with pytest.raises(ValidationError) as exc_info:
            AccessManagementUpdate(**update_data)
        
        assert "Note must be less than 200 characters" in str(exc_info.value)
