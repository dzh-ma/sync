"""
This module defines the EnergyData model used for storing energy consumption records

The model:
- Represents energy consumption data for a specific device
- Includes metadata such as timestamp & location
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EnergyData(BaseModel):
    """
    Pydantic model representing energy consumption data for a smart device

    Attributes:
        device_id (str): Unique identifier for the device
        timestamp (datetime): The date & time of the recorded energy consumption
        energy_consumed (float): The amount of energy consumed in kilowatt-hours (kWh)
        location (Optional[str]): The optional physical location of the device
    """
    device_id: str
    timestamp: datetime
    energy_consumed: float          # tracking in kWh (kilowatt hours)
    location: Optional[str] = None
