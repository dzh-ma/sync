"""
This module defines the Profile model for managing user profiles in the Smart Family Energy Manager

The Profile model:
- Represents different user types within the system (adult/elderly, child)
- Stores accessibility preferences & personalization settings
- Manages access control for features like device control & energy data
- Supports the admin's ability to create & manage multiple profiles per household
"""
from typing import Optional
from pydantic import BaseModel

class Profile(BaseModel):
    '''
    Pydantic model representing a user profile in the Smart Family Energy Manager system
    
    Profiles are created by an admin & can be customized for different family member
        with varying levels of access to system features & data
    
    Attributes:
        user_id (str): Unique identifier linking this profile to a user account
        name (str): The display name for this profile
        age (Optional[int]): The age of the profile user, used to tailor experience
        profile_type (str): Type of profile - "adult", "elderly", or "child"
        accessibility_settings (Dict): Dictionary containing accessibility preferences
        can_control_devices (bool): Whether this profile can control smart devices
        can_access_energy_data (bool): Whether this profile can view energy consumption data
        can_manage_notifications (bool): Whether this profile can manage notification settings
    '''
    user_id: str
    name: str
    age: Optional[str]
    profile_type: str       # "adult"/"elderly"/"child"
    accessibility_settings: dict = {}
    can_control_devices: bool = False
    can_access_energy_data: bool = False
    can_manage_notifications: bool = False
