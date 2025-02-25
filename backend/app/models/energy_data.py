"""
This module defines the EnergyData model used for storing energy consumption records

The model:
- Represents energy consumption data for a specific device
- Includes metadata such as timestamp & location
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class EnergyData(BaseModel):
    """
    Pydantic model representing energy consumption data for a smart device

    Attributes:
        device_id (str): Unique identifier for the device
        timestamp (List[datetime]): The dates & times of the recorded energy consumption
        energy_consumed (List[float]): The amount of energy consumed in kilowatt-hours (kWh)
        location (Optional[str]): The optional physical location of the device
        is_on (bool): Checks if the device is on/off
    """
    device_id: str
    timestamp: List[datetime]       # stores multiple timestamps
    energy_consumed: List[float]          # tracking in kWh (kilowatt hours)
    location: Optional[str] = None
    is_on: bool = Field(default = True)     # new field to track device state
