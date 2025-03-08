"""
This module defines the EnergySummary model for analyzing & reporting energy consumption

The EnergySummary model:
- Aggregates energy consumption data over specified time periods
- Supports reporting & historical data analysis requirements
- Enables cost estimation based on energy usage
- Facilitates comparisons between current & past usage periods
- Provides the data foundation for energy-saving suggestions & insights
"""
from typing import Optional
from pydantic import BaseModel

class Device(BaseModel):
    """
        Pydantic model representing a smart device within the home automation system
        
        Tracks device information, current status, & location within the home

        Used for device control, automation, & energy consumption tracking
        
        Attributes:
            id (str): Unique identifier for the device
            name (str): User-friendly name for the device
            type (str): Category of device (e.g., "light", "thermostat", "appliance")
            room_id (Optional[str]): ID of the room where the device is located
            status (str): Current operational status ("on", "off", or custom states)
            is_active (bool): Whether the device is currently available in the system
    """
    id: str
    name: str
    type: str
    room_id: Optional[str]
    status: str             # "on"/"off"/custom states
    is_active: bool = True
