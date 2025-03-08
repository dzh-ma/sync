"""
This module defines the Schedule model for automating device operations within the smart home

The Schedule model:
- Enables users to set timed operations for connected devices
- Supports the scheduling & automation functional requirements
- Allows for energy optimization through scheduled device usage
- Provides time-based control of devices for convenience & efficiency
- Implements the core functionality of device automation based on user-defined schedules
"""
from datetime import datetime
from pydantic import BaseModel

class Schedule(BaseModel):
    """
    Pydantic model representing an automated schedule for a smart device
    
    Allows users to create automated routines for devices to operate at
        specified times, supporting energy efficiency & convenience
    
    Attributes:
        device_id (str): ID of the device to be controlled by this schedule
        start_time (datetime): Time when the scheduled operation should begin
        end_time (datetime): Time when the scheduled operation should end
        start_date (datetime): Date when the schedule becomes active
        end_date (datetime): Date when the schedule expires
        created_by (str): ID of the user who created this schedule
        is_active (bool): Whether this schedule is currently enabled
    """
    device_id: str
    start_time: datetime
    end_time: datetime
    start_date: datetime
    end_date: datetime
    created_by: str         # user_id
    is_active: bool = True
