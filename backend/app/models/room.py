"""
This module defines the Room model for organizing smart devices by location within the home

The Room model:
- Provides a way to group devices by physical location
- Supports the add/delete room functionality requirement
- Enables room-based energy consumption analytics
- Helps users organize & manage their smart home more efficiently
- Facilitates location-specific automation rules & schedules
"""
from pydantic import BaseModel

class Room(BaseModel):
    """
    Pydantic model representing a room or area within the smart home
    
    Rooms provide organizational structure for devices & help contextualize
        energy usage data by location
    
    Attributes:
        id (str): Unique identifier for the room
        name (str): User-friendly name for the room (e.g., "Living Room", "Kitchen")
        created_by (str): ID of the user who created this room
    """
    id: str
    name: str
    created_by: str     # user_id
