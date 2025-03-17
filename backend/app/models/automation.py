"""
Models for automation validation.
"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator

class TriggerType(str, Enum):
    """
    Enum for different types of automation triggers.
    """
    TIME = "time"
    SENSOR = "sensor"
    MANUAL = "manual"
    DEVICE_STATE = "device_state"
    LOCATION = "location"
    WEATHER = "weather"

class ActionType(str, Enum):
    """
    Enum for different types of automation actions.
    """
    DEVICE_CONTROL = "device_control"
    NOTIFICATION = "notification"
    SCENE_ACTIVATION = "scene_activation"
    ENERGY_MANAGEMENT = "energy_management"

class CreateAutomation(BaseModel):
    """
    Model for automation creation input.

    Attributes:
        name (str): Name of the automation.
        description (str): Description of what the automation does.
        user_id (str): ID of the user who owns this automation.
        device_id (str): ID of the device associated with this automation.
        enabled (bool): Whether the automation is enabled.
        trigger_type (TriggerType): Type of trigger for this automation.
        trigger_data (Dict): Configuration data for the trigger.
        action_type (ActionType): Type of action for this automation.
        action_data (Dict): Configuration data for the action.
        conditions (Optional[List[Dict]]): Optional conditions that must be met.
    """
    name: str
    description: str
    user_id: str
    device_id: str  
    enabled: bool = True
    trigger_type: TriggerType
    trigger_data: Dict[str, Any]
    action_type: ActionType
    action_data: Dict[str, Any]
    conditions: Optional[List[Dict[str, Any]]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate automation name.

        Arguments:
            v (str): Name to be validated.

        Returns:
            str: Validated name.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if len(v) < 3:
            raise ValueError("Automation name must be at least 3 characters long.")
        if len(v) > 50:
            raise ValueError("Automation name must be less than 50 characters long.")

        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """
        Validate automation description.

        Arguments:
            v (str): Description to be validated.

        Returns:
            str: Validated description.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if len(v) > 500:
            raise ValueError("Automation description must be less than 500 characters long.")

        return v


# What gets stored in MongoDB
class AutomationDB(BaseModel):
    """
    Internal model representing automation data in the database.

    Attributes:
        id (str): Unique automation identifier.
        name (str): Name of the automation.
        description (str): Description of what the automation does.
        user_id (str): ID of the user who owns this automation.
        device_id (str): ID of the device associated with this automation.
        enabled (bool): Whether the automation is enabled.
        trigger_type (TriggerType): Type of trigger for this automation.
        trigger_data (Dict): Configuration data for the trigger.
        action_type (ActionType): Type of action for this automation.
        action_data (Dict): Configuration data for the action.
        conditions (Optional[List[Dict]]): Optional conditions that must be met.
        created (datetime): When the automation was created.
        updated (Optional[datetime]): When the automation was last updated.
        last_triggered (Optional[datetime]): When the automation was last triggered.
        execution_count (int): Number of times the automation has executed.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    user_id: str
    device_id: str
    enabled: bool = True
    trigger_type: TriggerType
    trigger_data: Dict[str, Any]
    action_type: ActionType
    action_data: Dict[str, Any]
    conditions: Optional[List[Dict[str, Any]]] = None
    created: datetime = Field(default_factory=datetime.utcnow)
    updated: Optional[datetime] = None
    last_triggered: Optional[datetime] = None
    execution_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# What gets returned in API responses
class AutomationResponse(BaseModel):
    """
    Model for automation data returned in API responses.

    Attributes:
        id (str): Unique automation identifier.
        name (str): Name of the automation.
        description (str): Description of what the automation does.
        user_id (str): ID of the user who owns this automation.
        device_id (str): ID of the device associated with this automation.
        enabled (bool): Whether the automation is enabled.
        trigger_type (TriggerType): Type of trigger for this automation.
        action_type (ActionType): Type of action for this automation.
        created (datetime): When the automation was created.
        last_triggered (Optional[datetime]): When the automation was last triggered.
        execution_count (int): Number of times the automation has executed.
    """
    id: str
    name: str
    description: str
    user_id: str
    device_id: str
    enabled: bool
    trigger_type: TriggerType
    action_type: ActionType
    created: datetime
    last_triggered: Optional[datetime] = None
    execution_count: int

    model_config = ConfigDict(from_attributes=True)


# For detailed API responses that include configuration data
class AutomationDetailResponse(AutomationResponse):
    """
    Detailed model for automation data returned in API responses.
    Extends AutomationResponse to include configuration details.

    Additional Attributes:
        trigger_data (Dict): Configuration data for the trigger.
        action_data (Dict): Configuration data for the action.
        conditions (Optional[List[Dict]]): Optional conditions that must be met.
        updated (Optional[datetime]): When the automation was last updated.
    """
    trigger_data: Dict[str, Any]
    action_data: Dict[str, Any]
    conditions: Optional[List[Dict[str, Any]]] = None
    updated: Optional[datetime] = None


# For updating automation information
class AutomationUpdate(BaseModel):
    """
    Model for updating automation information.

    Attributes:
        name (Optional[str]): Updated name of the automation.
        description (Optional[str]): Updated description.
        enabled (Optional[bool]): Updated enabled status.
        trigger_type (Optional[TriggerType]): Updated trigger type.
        trigger_data (Optional[Dict]): Updated trigger configuration.
        action_type (Optional[ActionType]): Updated action type.
        action_data (Optional[Dict]): Updated action configuration.
        conditions (Optional[List[Dict]]): Updated conditions.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    trigger_type: Optional[TriggerType] = None
    trigger_data: Optional[Dict[str, Any]] = None
    action_type: Optional[ActionType] = None
    action_data: Optional[Dict[str, Any]] = None
    conditions: Optional[List[Dict[str, Any]]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate automation name.

        Arguments:
            v (Optional[str]): Name to be validated.

        Returns:
            Optional[str]: Validated name.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if isinstance(v, str):
            if len(v) < 3:
                raise ValueError("Automation name must be at least 3 characters long.")
            if len(v) > 50:
                raise ValueError("Automation name must be less than 50 characters long.")

        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate automation description.

        Arguments:
            v (Optional[str]): Description to be validated.

        Returns:
            Optional[str]: Validated description.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if isinstance(v, str) and len(v) > 500:
            raise ValueError("Automation description must be less than 500 characters long.")

        return v
