"""
Tests for user profile validation & handling models.
"""
import uuid
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from app.models.profile import (  # Replace with your actual module name
    CreateProfile,
    ProfileDB,
    ProfileResponse,
    ProfileUpdate
)


class TestCreateProfile:
    """Test cases for the CreateProfile model."""

    def test_create_profile_minimal(self):
        """Test creating a profile with minimal required fields."""
        profile = CreateProfile(
            user_id="user123",
            first_name="John",
            last_name="Doe"
        )
        
        assert profile.user_id == "user123"
        assert profile.first_name == "John"
        assert profile.last_name == "Doe"
        assert profile.display_name is None
        assert profile.avatar is None
        assert profile.phone_number is None
        assert profile.timezone == "UTC"
        assert profile.temperature_unit == "C"
        assert profile.dark_mode is False

    def test_create_profile_full(self):
        """Test creating a profile with all fields."""
        profile = CreateProfile(
            user_id="user456",
            first_name="Jane",
            last_name="Smith",
            display_name="JaneS",
            avatar="https://example.com/avatar.jpg",
            phone_number="+1234567890",
            timezone="America/New_York",
            temperature_unit="F",
            dark_mode=True
        )
        
        assert profile.user_id == "user456"
        assert profile.first_name == "Jane"
        assert profile.last_name == "Smith"
        assert profile.display_name == "JaneS"
        assert profile.avatar == "https://example.com/avatar.jpg"
        assert profile.phone_number == "+1234567890"
        assert profile.timezone == "America/New_York"
        assert profile.temperature_unit == "F"
        assert profile.dark_mode is True

    def test_temperature_unit_validation(self):
        """Test temperature unit validation."""
        # Valid values
        CreateProfile(user_id="user1", first_name="John", last_name="Doe", temperature_unit="C")
        CreateProfile(user_id="user2", first_name="John", last_name="Doe", temperature_unit="F")
        
        # Invalid value
        with pytest.raises(ValidationError) as exc_info:
            CreateProfile(user_id="user3", first_name="John", last_name="Doe", temperature_unit="K")
        
        assert "Temperature unit must be either `C` or `F`" in str(exc_info.value)

    def test_timezone_validation(self):
        """Test timezone validation."""
        # Valid timezone
        CreateProfile(user_id="user1", first_name="John", last_name="Doe", timezone="Europe/London")
        
        # Empty timezone
        with pytest.raises(ValidationError) as exc_info:
            CreateProfile(user_id="user2", first_name="John", last_name="Doe", timezone="")
        
        assert "Timezone can't be empty" in str(exc_info.value)


class TestProfileDB:
    """Test cases for the ProfileDB model."""

    def test_profile_db_creation(self):
        """Test creating a ProfileDB instance."""
        before = datetime.utcnow()
        profile_db = ProfileDB(
            user_id="user789",
            first_name="Alex",
            last_name="Johnson"
        )
        after = datetime.utcnow()
        
        # Check required fields
        assert profile_db.user_id == "user789"
        assert profile_db.first_name == "Alex"
        assert profile_db.last_name == "Johnson"
        
        # Check default values
        assert profile_db.display_name is None
        assert profile_db.avatar is None
        assert profile_db.phone_number is None
        assert profile_db.timezone == "UTC"
        assert profile_db.temperature_unit == "C"
        assert profile_db.dark_mode is False
        assert profile_db.favorite_devices == []
        
        # Check auto-generated fields
        assert uuid.UUID(profile_db.id, version=4)  # Verify it's a valid UUID
        assert before <= profile_db.created <= after
        assert profile_db.updated is None

    def test_profile_db_all_fields(self):
        """Test creating a ProfileDB with all fields specified."""
        favorite_devices = ["device1", "device2"]
        created_time = datetime.utcnow() - timedelta(days=10)
        updated_time = datetime.utcnow() - timedelta(days=5)
        
        profile_db = ProfileDB(
            id="custom-id-123",
            user_id="user101",
            first_name="Sarah",
            last_name="Davis",
            display_name="SarahD",
            avatar="https://example.com/sarah.jpg",
            phone_number="+9876543210",
            timezone="Asia/Tokyo",
            temperature_unit="F",
            dark_mode=True,
            favorite_devices=favorite_devices,
            created=created_time,
            updated=updated_time
        )
        
        assert profile_db.id == "custom-id-123"
        assert profile_db.user_id == "user101"
        assert profile_db.first_name == "Sarah"
        assert profile_db.last_name == "Davis"
        assert profile_db.display_name == "SarahD"
        assert profile_db.avatar == "https://example.com/sarah.jpg"
        assert profile_db.phone_number == "+9876543210"
        assert profile_db.timezone == "Asia/Tokyo"
        assert profile_db.temperature_unit == "F"
        assert profile_db.dark_mode is True
        assert profile_db.favorite_devices == favorite_devices
        assert profile_db.created == created_time
        assert profile_db.updated == updated_time


class TestProfileResponse:
    """Test cases for the ProfileResponse model."""

    def test_profile_response_creation(self):
        """Test creating a ProfileResponse instance."""
        profile_response = ProfileResponse(
            id="response-id-123",
            user_id="user202",
            first_name="Michael",
            last_name="Brown",
            display_name="MikeB",
            avatar="https://example.com/mike.jpg",
            timezone="Australia/Sydney",
            temperature_unit="C",
            dark_mode=True,
            favorite_devices=["device3", "device4"]
        )
        
        assert profile_response.id == "response-id-123"
        assert profile_response.user_id == "user202"
        assert profile_response.first_name == "Michael"
        assert profile_response.last_name == "Brown"
        assert profile_response.display_name == "MikeB"
        assert profile_response.avatar == "https://example.com/mike.jpg"
        assert profile_response.timezone == "Australia/Sydney"
        assert profile_response.temperature_unit == "C"
        assert profile_response.dark_mode is True
        assert profile_response.favorite_devices == ["device3", "device4"]

    def test_profile_response_from_db(self):
        """Test creating a ProfileResponse from a ProfileDB instance."""
        # Create a ProfileDB instance
        profile_db = ProfileDB(
            id="db-id-456",
            user_id="user303",
            first_name="Emily",
            last_name="Wilson",
            display_name="EmilyW",
            avatar="https://example.com/emily.jpg",
            phone_number="+1122334455",  # This field won't be included in the response
            timezone="Europe/Berlin",
            temperature_unit="F",
            dark_mode=False,
            favorite_devices=["device5"]
        )
        
        # Create a ProfileResponse from the ProfileDB
        profile_response = ProfileResponse.model_validate(profile_db)
        
        # Check that fields are correctly transferred
        assert profile_response.id == profile_db.id
        assert profile_response.user_id == profile_db.user_id
        assert profile_response.first_name == profile_db.first_name
        assert profile_response.last_name == profile_db.last_name
        assert profile_response.display_name == profile_db.display_name
        assert profile_response.avatar == profile_db.avatar
        assert profile_response.timezone == profile_db.timezone
        assert profile_response.temperature_unit == profile_db.temperature_unit
        assert profile_response.dark_mode == profile_db.dark_mode
        assert profile_response.favorite_devices == profile_db.favorite_devices
        
        # Check that phone_number is not in ProfileResponse
        with pytest.raises(AttributeError):
            profile_response.phone_number


class TestProfileUpdate:
    """Test cases for the ProfileUpdate model."""

    def test_profile_update_empty(self):
        """Test creating an empty update (all fields None)."""
        profile_update = ProfileUpdate()
        
        assert profile_update.first_name is None
        assert profile_update.last_name is None
        assert profile_update.display_name is None
        assert profile_update.avatar is None
        assert profile_update.phone_number is None
        assert profile_update.timezone is None
        assert profile_update.temperature_unit is None
        assert profile_update.dark_mode is None
        assert profile_update.favorite_devices is None

    def test_profile_update_partial(self):
        """Test updating only some fields."""
        profile_update = ProfileUpdate(
            first_name="NewName",
            avatar="https://example.com/new-avatar.jpg",
            temperature_unit="F"
        )
        
        assert profile_update.first_name == "NewName"
        assert profile_update.avatar == "https://example.com/new-avatar.jpg"
        assert profile_update.temperature_unit == "F"
        
        # Other fields should still be None
        assert profile_update.last_name is None
        assert profile_update.display_name is None
        assert profile_update.phone_number is None
        assert profile_update.timezone is None
        assert profile_update.dark_mode is None
        assert profile_update.favorite_devices is None

    def test_temperature_unit_validation(self):
        """Test temperature unit validation in updates."""
        # Valid values
        ProfileUpdate(temperature_unit="C")
        ProfileUpdate(temperature_unit="F")
        ProfileUpdate(temperature_unit=None)  # None is valid for updates
        
        # Invalid value
        with pytest.raises(ValidationError) as exc_info:
            ProfileUpdate(temperature_unit="Kelvin")
        
        assert "Temperature unit must either be `C` or `F`" in str(exc_info.value)

    def test_timezone_validation(self):
        """Test timezone validation in updates."""
        # Valid values
        ProfileUpdate(timezone="America/Chicago")
        ProfileUpdate(timezone=None)  # None is valid for updates
        
        # Invalid: empty string
        with pytest.raises(ValidationError) as exc_info:
            ProfileUpdate(timezone="")
        
        assert "Timezone can't be an empty string" in str(exc_info.value)
