"""
Unit tests for suggestion models.
"""
import uuid
from datetime import datetime, timedelta
import pytest
from pydantic import ValidationError

from app.models.suggestion import (
    CreateSuggestion, 
    SuggestionDB, 
    SuggestionResponse, 
    SuggestionUpdate,
    SuggestionStatus,
    SuggestionType
)

def test_create_suggestion_valid():
    """Test creating a valid suggestion."""
    user_id = str(uuid.uuid4())
    device_id = str(uuid.uuid4())
    
    suggestion = CreateSuggestion(
        user_id=user_id,
        title="Lower thermostat at night",
        description="Automatically lower the thermostat by 3 degrees at 11pm to save energy while sleeping.",
        type=SuggestionType.ENERGY_SAVING,
        priority=4,
        related_device_ids=[device_id]
    )
    
    assert suggestion.user_id == user_id
    assert suggestion.title == "Lower thermostat at night"
    assert suggestion.type == SuggestionType.ENERGY_SAVING
    assert suggestion.priority == 4
    assert device_id in suggestion.related_device_ids

def test_create_suggestion_defaults():
    """Test default values in CreateSuggestion."""
    user_id = str(uuid.uuid4())
    
    suggestion = CreateSuggestion(
        user_id=user_id,
        title="Security camera adjustment",
        description="Adjust the angle of your front door camera to better capture visitor faces.",
        type=SuggestionType.SECURITY
    )
    
    assert suggestion.priority == 3  # Default priority
    assert suggestion.related_device_ids is None

def test_create_suggestion_invalid_title():
    """Test validation for invalid title."""
    user_id = str(uuid.uuid4())
    
    # Title too short
    with pytest.raises(ValidationError) as exc_info:
        CreateSuggestion(
            user_id=user_id,
            title="AB",  # Too short
            description="This is a proper description for testing.",
            type=SuggestionType.OTHER
        )
    assert "Title must be at least 3 characters long" in str(exc_info.value)
    
    # Title too long
    with pytest.raises(ValidationError) as exc_info:
        CreateSuggestion(
            user_id=user_id,
            title="A" * 101,  # Too long
            description="This is a proper description for testing.",
            type=SuggestionType.OTHER
        )
    assert "Title must be less than 100 characters long" in str(exc_info.value)

def test_create_suggestion_invalid_description():
    """Test validation for invalid description."""
    user_id = str(uuid.uuid4())
    
    # Description too short
    with pytest.raises(ValidationError) as exc_info:
        CreateSuggestion(
            user_id=user_id,
            title="Valid Title",
            description="Too short",  # Too short
            type=SuggestionType.COMFORT
        )
    assert "Description must be at least 10 characters long" in str(exc_info.value)

def test_create_suggestion_invalid_priority():
    """Test validation for invalid priority."""
    user_id = str(uuid.uuid4())
    
    # Priority too low
    with pytest.raises(ValidationError) as exc_info:
        CreateSuggestion(
            user_id=user_id,
            title="Valid Title",
            description="This is a proper description for testing.",
            type=SuggestionType.AUTOMATION,
            priority=0  # Invalid
        )
    assert "Priority must be between 1 and 5" in str(exc_info.value)
    
    # Priority too high
    with pytest.raises(ValidationError) as exc_info:
        CreateSuggestion(
            user_id=user_id,
            title="Valid Title",
            description="This is a proper description for testing.",
            type=SuggestionType.AUTOMATION,
            priority=6  # Invalid
        )
    assert "Priority must be between 1 and 5" in str(exc_info.value)

def test_create_suggestion_invalid_user_id():
    """Test validation for invalid user_id."""
    with pytest.raises(ValidationError) as exc_info:
        CreateSuggestion(
            user_id="not-a-valid-uuid",
            title="Valid Title",
            description="This is a proper description for testing.",
            type=SuggestionType.ENERGY_SAVING
        )
    assert "Invalid user_id format" in str(exc_info.value)

def test_create_suggestion_invalid_device_ids():
    """Test validation for invalid device_ids."""
    user_id = str(uuid.uuid4())
    valid_device_id = str(uuid.uuid4())
    
    with pytest.raises(ValidationError) as exc_info:
        CreateSuggestion(
            user_id=user_id,
            title="Valid Title",
            description="This is a proper description for testing.",
            type=SuggestionType.ENERGY_SAVING,
            related_device_ids=[valid_device_id, "not-a-valid-uuid"]
        )
    assert "Invalid device ID format" in str(exc_info.value)

def test_suggestion_db_model():
    """Test SuggestionDB model."""
    user_id = str(uuid.uuid4())
    device_id = str(uuid.uuid4())
    
    suggestion_db = SuggestionDB(
        user_id=user_id,
        title="Motion lighting",
        description="Set up motion sensors to automatically turn on hallway lights at night.",
        type=SuggestionType.AUTOMATION,
        priority=5,
        related_device_ids=[device_id]
    )
    
    assert isinstance(suggestion_db.id, str)
    # Try parsing to ensure it's a valid UUID
    uuid.UUID(suggestion_db.id)
    assert suggestion_db.user_id == user_id
    assert suggestion_db.status == SuggestionStatus.PENDING
    assert isinstance(suggestion_db.created, datetime)
    assert suggestion_db.updated is None
    assert suggestion_db.implemented_date is None
    assert suggestion_db.user_feedback is None

def test_suggestion_response_model():
    """Test SuggestionResponse model."""
    user_id = str(uuid.uuid4())
    suggestion_id = str(uuid.uuid4())
    created_time = datetime.utcnow()
    
    suggestion_response = SuggestionResponse(
        id=suggestion_id,
        user_id=user_id,
        title="Smart water monitoring",
        description="Install water sensors to detect leaks before they cause damage.",
        type=SuggestionType.SECURITY,
        priority=5,
        status=SuggestionStatus.ACCEPTED,
        created=created_time
    )
    
    assert suggestion_response.id == suggestion_id
    assert suggestion_response.user_id == user_id
    assert suggestion_response.title == "Smart water monitoring"
    assert suggestion_response.status == SuggestionStatus.ACCEPTED
    assert suggestion_response.implemented_date is None

def test_suggestion_update_model():
    """Test SuggestionUpdate model with valid data."""
    update_data = SuggestionUpdate(
        title="Updated title",
        priority=2,
        status=SuggestionStatus.IMPLEMENTED,
        user_feedback="This was very helpful, thank you!"
    )
    
    assert update_data.title == "Updated title"
    assert update_data.description is None
    assert update_data.priority == 2
    assert update_data.status == SuggestionStatus.IMPLEMENTED
    assert update_data.user_feedback == "This was very helpful, thank you!"

def test_suggestion_update_invalid_title():
    """Test SuggestionUpdate with invalid title."""
    with pytest.raises(ValidationError) as exc_info:
        SuggestionUpdate(title="AB")  # Too short
    assert "Title must be at least 3 characters long" in str(exc_info.value)

def test_suggestion_update_invalid_description():
    """Test SuggestionUpdate with invalid description."""
    with pytest.raises(ValidationError) as exc_info:
        SuggestionUpdate(description="Too short")  # Too short
    assert "Description must be at least 10 characters long" in str(exc_info.value)

def test_suggestion_update_invalid_priority():
    """Test SuggestionUpdate with invalid priority."""
    with pytest.raises(ValidationError) as exc_info:
        SuggestionUpdate(priority=0)  # Invalid
    assert "Priority must be between 1 and 5" in str(exc_info.value)

def test_suggestion_update_invalid_feedback():
    """Test SuggestionUpdate with too long feedback."""
    with pytest.raises(ValidationError) as exc_info:
        SuggestionUpdate(user_feedback="A" * 501)  # Too long
    assert "Feedback must be less than 500 characters long" in str(exc_info.value)

def test_implementation_date_update():
    """Test updating implementation date when status changes to implemented."""
    # This would typically be handled in your service layer, but testing the models here
    
    user_id = str(uuid.uuid4())
    
    # Create a suggestion
    suggestion_db = SuggestionDB(
        user_id=user_id,
        title="Schedule vacuum",
        description="Schedule robot vacuum to run while you're at work.",
        type=SuggestionType.AUTOMATION,
        priority=3,
        status=SuggestionStatus.ACCEPTED,
    )
    
    # Update status to implemented
    suggestion_db.status = SuggestionStatus.IMPLEMENTED
    suggestion_db.implemented_date = datetime.utcnow()
    suggestion_db.updated = datetime.utcnow()
    
    assert suggestion_db.status == SuggestionStatus.IMPLEMENTED
    assert isinstance(suggestion_db.implemented_date, datetime)
    assert isinstance(suggestion_db.updated, datetime)
