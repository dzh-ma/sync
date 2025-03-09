"""
This module contains business logic for CRUD operations on various entities:
- Devices
- Profiles
- Rooms
- Schedules

It also includes functions for energy data aggregation and summary generation
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union, Any
from bson import ObjectId
from fastapi import HTTPException, status

# Import models
from app.models.device import Device
from app.models.profile import Profile
from app.models.room import Room
from app.models.schedule import Schedule
from app.models.energy_data import EnergyData
from app.models.energy_summary import EnergySummary

# Import database connections
from app.db.database import (
    devices_collection,
    profiles_collection,
    rooms_collection,
    schedules_collection,
    energy_collection,
    summary_collection
)

# ----- Device Operations -----

async def create_device(device: Device) -> Dict:
    """
    Create a new device in the database.
    
    Args:
        device (Device): The device to create
        
    Returns:
        Dict: The created device
        
    Raises:
        HTTPException: If there's an issue creating the device
    """
    try:
        # Check if device with same ID already exists
        if devices_collection.find_one({"id": device.id}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Device with ID {device.id} already exists"
            )
            
        # Insert device into database
        device_dict = device.model_dump()
        result = devices_collection.insert_one(device_dict)
        
        if not result.acknowledged:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create device"
            )
            
        # Return the created device
        return device_dict
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating device: {str(e)}"
        )

async def get_device(device_id: str) -> Dict:
    """
    Get a device by its ID.
    
    Args:
        device_id (str): The ID of the device to retrieve
        
    Returns:
        Dict: The device data
        
    Raises:
        HTTPException: If the device is not found
    """
    device = devices_collection.find_one({"id": device_id})
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    return device

async def get_devices(room_id: Optional[str] = None) -> List[Dict]:
    """
    Get all devices, optionally filtered by room.
    
    Args:
        room_id (Optional[str]): The room ID to filter by
        
    Returns:
        List[Dict]: A list of devices
    """
    query = {}
    if room_id:
        query["room_id"] = room_id
        
    devices = list(devices_collection.find(query))
    return devices

async def update_device(device_id: str, device_data: Dict) -> Dict:
    """
    Update a device.
    
    Args:
        device_id (str): The ID of the device to update
        device_data (Dict): The updated device data
        
    Returns:
        Dict: The updated device
        
    Raises:
        HTTPException: If the device is not found or update fails
    """
    # Check if device exists
    existing_device = await get_device(device_id)
    
    # Remove ID field from update data if present
    if "id" in device_data:
        del device_data["id"]
        
    # Update timestamp
    device_data["updated_at"] = datetime.now(timezone.utc)
    
    # Update the device
    result = devices_collection.update_one(
        {"id": device_id},
        {"$set": device_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update device with ID {device_id}"
        )
        
    # Return updated device
    return {**existing_device, **device_data}

async def delete_device(device_id: str) -> Dict:
    """
    Delete a device.
    
    Args:
        device_id (str): The ID of the device to delete
        
    Returns:
        Dict: A success message
        
    Raises:
        HTTPException: If the device is not found or deletion fails
    """
    # Check if device exists
    await get_device(device_id)
    
    # Delete the device
    result = devices_collection.delete_one({"id": device_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete device with ID {device_id}"
        )
        
    # Also delete any schedules associated with this device
    schedules_collection.delete_many({"device_id": device_id})
    
    return {"message": f"Device with ID {device_id} deleted successfully"}

# ----- Profile Operations -----

async def create_profile(profile: Profile) -> Dict:
    """
    Create a new profile for a user.
    
    Args:
        profile (Profile): The profile to create
        
    Returns:
        Dict: The created profile
        
    Raises:
        HTTPException: If there's an issue creating the profile
    """
    try:
        # Check if profile with same name already exists for this user
        if profiles_collection.find_one({"user_id": profile.user_id, "name": profile.name}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Profile with name '{profile.name}' already exists for this user"
            )
            
        # Insert profile into database
        profile_dict = profile.model_dump()
        profile_dict["created_at"] = datetime.now(timezone.utc)
        profile_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = profiles_collection.insert_one(profile_dict)
        
        if not result.acknowledged:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create profile"
            )
            
        # Add the MongoDB ID to the profile
        profile_dict["_id"] = str(result.inserted_id)
            
        return profile_dict
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating profile: {str(e)}"
        )

async def get_profile(profile_id: str) -> Dict:
    """
    Get a profile by its ID.
    
    Args:
        profile_id (str): The ID of the profile to retrieve
        
    Returns:
        Dict: The profile data
        
    Raises:
        HTTPException: If the profile is not found
    """
    try:
        profile = profiles_collection.find_one({"_id": ObjectId(profile_id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile with ID {profile_id} not found"
            )
            
        # Convert ObjectId to string
        profile["_id"] = str(profile["_id"])
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profile: {str(e)}"
        )

async def get_user_profiles(user_id: str) -> List[Dict]:
    """
    Get all profiles for a specific user.
    
    Args:
        user_id (str): The user ID to get profiles for
        
    Returns:
        List[Dict]: A list of profiles
    """
    try:
        profiles = list(profiles_collection.find({"user_id": user_id}))
        
        # Convert ObjectId to string for each profile
        for profile in profiles:
            profile["_id"] = str(profile["_id"])
            
        return profiles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profiles: {str(e)}"
        )

async def update_profile(profile_id: str, profile_data: Dict) -> Dict:
    """
    Update a profile.
    
    Args:
        profile_id (str): The ID of the profile to update
        profile_data (Dict): The updated profile data
        
    Returns:
        Dict: The updated profile
        
    Raises:
        HTTPException: If the profile is not found or update fails
    """
    try:
        # Check if profile exists
        existing_profile = await get_profile(profile_id)
        
        # Update timestamp
        profile_data["updated_at"] = datetime.now(timezone.utc)
        
        # Update the profile
        result = profiles_collection.update_one(
            {"_id": ObjectId(profile_id)},
            {"$set": profile_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update profile with ID {profile_id}"
            )
            
        # Return updated profile
        return {**existing_profile, **profile_data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )

async def delete_profile(profile_id: str) -> Dict:
    """
    Delete a profile.
    
    Args:
        profile_id (str): The ID of the profile to delete
        
    Returns:
        Dict: A success message
        
    Raises:
        HTTPException: If the profile is not found or deletion fails
    """
    try:
        # Check if profile exists
        await get_profile(profile_id)
        
        # Delete the profile
        result = profiles_collection.delete_one({"_id": ObjectId(profile_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to delete profile with ID {profile_id}"
            )
            
        return {"message": f"Profile with ID {profile_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting profile: {str(e)}"
        )

# ----- Room Operations -----

async def create_room(room: Room) -> Dict:
    """
    Create a new room.
    
    Args:
        room (Room): The room to create
        
    Returns:
        Dict: The created room
        
    Raises:
        HTTPException: If there's an issue creating the room
    """
    try:
        # Check if room with same ID already exists
        if rooms_collection.find_one({"id": room.id}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Room with ID {room.id} already exists"
            )
            
        # Insert room into database
        room_dict = room.model_dump()
        room_dict["created_at"] = datetime.now(timezone.utc)
        
        result = rooms_collection.insert_one(room_dict)
        
        if not result.acknowledged:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create room"
            )
            
        return room_dict
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating room: {str(e)}"
        )

async def get_room(room_id: str) -> Dict:
    """
    Get a room by its ID.
    
    Args:
        room_id (str): The ID of the room to retrieve
        
    Returns:
        Dict: The room data
        
    Raises:
        HTTPException: If the room is not found
    """
    room = rooms_collection.find_one({"id": room_id})
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    return room

async def get_user_rooms(user_id: str) -> List[Dict]:
    """
    Get all rooms created by a specific user.
    
    Args:
        user_id (str): The user ID to get rooms for
        
    Returns:
        List[Dict]: A list of rooms
    """
    rooms = list(rooms_collection.find({"created_by": user_id}))
    return rooms

async def update_room(room_id: str, room_data: Dict) -> Dict:
    """
    Update a room.
    
    Args:
        room_id (str): The ID of the room to update
        room_data (Dict): The updated room data
        
    Returns:
        Dict: The updated room
        
    Raises:
        HTTPException: If the room is not found or update fails
    """
    # Check if room exists
    existing_room = await get_room(room_id)
    
    # Prevent ID field from being updated
    if "id" in room_data:
        del room_data["id"]
        
    # Update the room
    result = rooms_collection.update_one(
        {"id": room_id},
        {"$set": room_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update room with ID {room_id}"
        )
        
    # Return updated room
    return {**existing_room, **room_data}

async def delete_room(room_id: str) -> Dict:
    """
    Delete a room.
    
    Args:
        room_id (str): The ID of the room to delete
        
    Returns:
        Dict: A success message
        
    Raises:
        HTTPException: If the room is not found or deletion fails
    """
    # Check if room exists
    await get_room(room_id)
    
    # Get all devices in this room
    devices_in_room = await get_devices(room_id)
    
    # Update devices to remove room association
    for device in devices_in_room:
        await update_device(device["id"], {"room_id": None})
    
    # Delete the room
    result = rooms_collection.delete_one({"id": room_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete room with ID {room_id}"
        )
        
    return {"message": f"Room with ID {room_id} deleted successfully"}

# ----- Schedule Operations -----

async def create_schedule(schedule: Schedule) -> Dict:
    """
    Create a new schedule for a device.
    
    Args:
        schedule (Schedule): The schedule to create
        
    Returns:
        Dict: The created schedule
        
    Raises:
        HTTPException: If there's an issue creating the schedule
    """
    try:
        # Check if device exists
        await get_device(schedule.device_id)
        
        # Insert schedule into database
        schedule_dict = schedule.model_dump()
        schedule_dict["created_at"] = datetime.now(timezone.utc)
        
        result = schedules_collection.insert_one(schedule_dict)
        
        if not result.acknowledged:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create schedule"
            )
            
        # Add the MongoDB ID to the schedule
        schedule_dict["_id"] = str(result.inserted_id)
            
        return schedule_dict
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating schedule: {str(e)}"
        )

async def get_schedule(schedule_id: str) -> Dict:
    """
    Get a schedule by its ID.
    
    Args:
        schedule_id (str): The ID of the schedule to retrieve
        
    Returns:
        Dict: The schedule data
        
    Raises:
        HTTPException: If the schedule is not found
    """
    try:
        schedule = schedules_collection.find_one({"_id": ObjectId(schedule_id)})
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule with ID {schedule_id} not found"
            )
            
        # Convert ObjectId to string
        schedule["_id"] = str(schedule["_id"])
        return schedule
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving schedule: {str(e)}"
        )

async def get_device_schedules(device_id: str) -> List[Dict]:
    """
    Get all schedules for a specific device.
    
    Args:
        device_id (str): The device ID to get schedules for
        
    Returns:
        List[Dict]: A list of schedules
    """
    try:
        schedules = list(schedules_collection.find({"device_id": device_id}))
        
        # Convert ObjectId to string for each schedule
        for schedule in schedules:
            schedule["_id"] = str(schedule["_id"])
            
        return schedules
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving schedules: {str(e)}"
        )

async def get_user_schedules(user_id: str) -> List[Dict]:
    """
    Get all schedules created by a specific user.
    
    Args:
        user_id (str): The user ID to get schedules for
        
    Returns:
        List[Dict]: A list of schedules
    """
    try:
        schedules = list(schedules_collection.find({"created_by": user_id}))
        
        # Convert ObjectId to string for each schedule
        for schedule in schedules:
            schedule["_id"] = str(schedule["_id"])
            
        return schedules
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving schedules: {str(e)}"
        )

async def update_schedule(schedule_id: str, schedule_data: Dict) -> Dict:
    """
    Update a schedule.
    
    Args:
        schedule_id (str): The ID of the schedule to update
        schedule_data (Dict): The updated schedule data
        
    Returns:
        Dict: The updated schedule
        
    Raises:
        HTTPException: If the schedule is not found or update fails
    """
    try:
        # Check if schedule exists
        existing_schedule = await get_schedule(schedule_id)
        
        # Update the schedule
        result = schedules_collection.update_one(
            {"_id": ObjectId(schedule_id)},
            {"$set": schedule_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update schedule with ID {schedule_id}"
            )
            
        # Return updated schedule
        return {**existing_schedule, **schedule_data}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating schedule: {str(e)}"
        )

async def delete_schedule(schedule_id: str) -> Dict:
    """
    Delete a schedule.
    
    Args:
        schedule_id (str): The ID of the schedule to delete
        
    Returns:
        Dict: A success message
        
    Raises:
        HTTPException: If the schedule is not found or deletion fails
    """
    try:
        # Check if schedule exists
        await get_schedule(schedule_id)
        
        # Delete the schedule
        result = schedules_collection.delete_one({"_id": ObjectId(schedule_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to delete schedule with ID {schedule_id}"
            )
            
        return {"message": f"Schedule with ID {schedule_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting schedule: {str(e)}"
        )

# ----- Energy Summary Operations -----

async def generate_energy_summary(
    user_id: str, 
    period: str, 
    start_date: datetime,
    end_date: datetime
) -> Dict:
    """
    Generate an energy consumption summary for a specific period.
    
    Args:
        user_id (str): The user ID to generate the summary for
        period (str): The period type ("daily", "weekly", "monthly")
        start_date (datetime): The start date of the period
        end_date (datetime): The end date of the period
        
    Returns:
        Dict: The generated energy summary
        
    Raises:
        HTTPException: If there's an issue generating the summary
    """
    try:
        # Query energy data for the specified period
        query = {
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        # Get energy data for this period
        energy_data = list(energy_collection.find(query))
        
        if not energy_data:
            # Create an empty summary if no data exists
            summary = EnergySummary(
                user_id=user_id,
                period=period,
                start_date=start_date,
                end_date=end_date,
                total_consumption=0.0,
                cost_estimate=0.0,
                comparison_to_previous=0.0
            )
            summary_dict = summary.model_dump()
            return summary_dict
            
        # Calculate total consumption
        total_consumption = sum(data.get("energy_consumed", 0) for data in energy_data)
        
        # Estimate cost (simplified calculation - $0.15 per kWh)
        cost_estimate = total_consumption * 0.15
        
        # Calculate comparison to previous period
        previous_start = start_date - (end_date - start_date)
        previous_end = start_date
        
        previous_query = {
            "timestamp": {
                "$gte": previous_start,
                "$lte": previous_end
            }
        }
        
        previous_data = list(energy_collection.find(previous_query))
        previous_consumption = sum(data.get("energy_consumed", 0) for data in previous_data)
        
        # Calculate percentage change
        if previous_consumption > 0:
            comparison = ((total_consumption - previous_consumption) / previous_consumption) * 100
        else:
            comparison = 0.0
            
        # Create and save the summary
        summary = EnergySummary(
            user_id=user_id,
            period=period,
            start_date=start_date,
            end_date=end_date,
            total_consumption=total_consumption,
            cost_estimate=cost_estimate,
            comparison_to_previous=comparison
        )
        
        summary_dict = summary.model_dump()
        
        # Check if a summary already exists for this period
        existing_summary = summary_collection.find_one({
            "user_id": user_id,
            "period": period,
            "start_date": start_date
        })
        
        if existing_summary:
            # Update existing summary
            summary_collection.update_one(
                {"_id": existing_summary["_id"]},
                {"$set": summary_dict}
            )
        else:
            # Insert new summary
            summary_collection.insert_one(summary_dict)
            
        return summary_dict
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating energy summary: {str(e)}"
        )

async def get_user_energy_summaries(
    user_id: str,
    period: Optional[str] = None,
    limit: int = 10
) -> List[Dict]:
    """
    Get energy summaries for a specific user.
    
    Args:
        user_id (str): The user ID to get summaries for
        period (Optional[str]): Filter by period type (daily, weekly, monthly)
        limit (int): Maximum number of summaries to return
        
    Returns:
        List[Dict]: A list of energy summaries
    """
    try:
        query = {"user_id": user_id}
        
        if period:
            query["period"] = period
            
        # Sort by date descending to get the most recent summaries
        summaries = list(summary_collection.find(query).sort("end_date", -1).limit(limit))
        
        # Convert ObjectId to string for each summary
        for summary in summaries:
            if "_id" in summary:
                summary["_id"] = str(summary["_id"])
            
        return summaries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving energy summaries: {str(e)}"
        )

async def aggregate_energy_data_by_device(
    start_date: datetime, 
    end_date: datetime
) -> List[Dict]:
    """
    Aggregate energy consumption data by device.
    
    Args:
        start_date (datetime): The start date for the aggregation
        end_date (datetime): The end date for the aggregation
        
    Returns:
        List[Dict]: Aggregated energy data by device
    """
    try:
        pipeline = [
            {
                "$match": {
                    "timestamp": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": "$device_id",
                    "total_consumption": {"$sum": "$energy_consumed"},
                    "count": {"$sum": 1},
                    "avg_consumption": {"$avg": "$energy_consumed"},
                    "first_reading": {"$min": "$timestamp"},
                    "last_reading": {"$max": "$timestamp"}
                }
            },
            {
                "$sort": {"total_consumption": -1}
            }
        ]
        
        result = list(energy_collection.aggregate(pipeline))
        
        # Format the result
        for item in result:
            item["device_id"] = item.pop("_id")
            
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error aggregating energy data: {str(e)}"
        )

async def aggregate_energy_data_by_room(
    start_date: datetime, 
    end_date: datetime
) -> List[Dict]:
    """
    Aggregate energy consumption data by room.
    
    Args:
        start_date (datetime): The start date for the aggregation
        end_date (datetime): The end date for the aggregation
        
    Returns:
        List[Dict]: Aggregated energy data by room
    """
    try:
        # First, get all energy data for the time period
        query = {
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        energy_data = list(energy_collection.find(query))
        
        # Get device details to determine room
        all_devices = list(devices_collection.find())
        device_room_map = {device["id"]: device.get("room_id") for device in all_devices}
        
        # Get room details
        all_rooms = list(rooms_collection.find())
        room_map = {room["id"]: room["name"] for room in all_rooms}
        
        # Organize data by room
        room_consumption = {}
        
        for data in energy_data:
            device_id = data.get("device_id")
            room_id = device_room_map.get(device_id)
            
            # Skip if device is not assigned to a room
            if not room_id:
                continue
                
            room_name = room_map.get(room_id, "Unknown Room")
            
            if room_name not in room_consumption:
                room_consumption[room_name] = {
                    "room_id": room_id,
                    "room_name": room_name,
                    "total_consumption": 0,
                    "device_count": set()
                }
                
            room_consumption[room_name]["total_consumption"] += data.get("energy_consumed", 0)
            room_consumption[room_name]["device_count"].add(device_id)
            
        # Convert to list and format the output
        result = []
        for room_name, data in room_consumption.items():
            result.append({
                "room_id": data["room_id"],
                "room_name": room_name,
                "total_consumption": data["total_consumption"],
                "device_count": len(data["device_count"])
            })
            
        # Sort by total consumption descending
        result.sort(key=lambda x: x["total_consumption"], reverse=True)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error aggregating energy data by room: {str(e)}"
        )

async def generate_daily_summaries(user_id: str, days: int = 7) -> List[Dict]:
    """
    Generate daily energy summaries for the past specified number of days.
    
    Args:
        user_id (str): The user ID to generate summaries for
        days (int): Number of past days to generate summaries for
        
    Returns:
        List[Dict]: The generated daily summaries
    """
    try:
        summaries = []
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(days):
            end_date = today - timedelta(days=i)
            start_date = end_date - timedelta(days=1)
            
            summary = await generate_energy_summary(
                user_id=user_id,
                period="daily",
                start_date=start_date,
                end_date=end_date
            )
            
            summaries.append(summary)
        
        return summaries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating daily summaries: {str(e)}"
        )

async def generate_weekly_summary(user_id: str) -> Dict:
    """
    Generate a weekly energy summary for the current week.
    
    Args:
        user_id (str): The user ID to generate the summary for
        
    Returns:
        Dict: The generated weekly summary
    """
    try:
        # Calculate the start and end dates for the current week
        today = datetime.now(timezone.utc)
        start_of_week = today - timedelta(days=today.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=7)
        
        summary = await generate_energy_summary(
            user_id=user_id,
            period="weekly",
            start_date=start_of_week,
            end_date=end_of_week
        )
        
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating weekly summary: {str(e)}"
        )

async def generate_monthly_summary(user_id: str) -> Dict:
    """
    Generate a monthly energy summary for the current month.
    
    Args:
        user_id (str): The user ID to generate the summary for
        
    Returns:
        Dict: The generated monthly summary
    """
    try:
        # Calculate the start and end dates for the current month
        today = datetime.now(timezone.utc)
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate the first day of next month
        if today.month == 12:
            end_of_month = today.replace(year=today.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            end_of_month = today.replace(month=today.month+1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        summary = await generate_energy_summary(
            user_id=user_id,
            period="monthly",
            start_date=start_of_month,
            end_date=end_of_month
        )
        
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating monthly summary: {str(e)}"
        )

async def get_energy_usage_trends(user_id: str, period_type: str, num_periods: int = 6) -> List[Dict]:
    """
    Get energy usage trends over time.
    
    Args:
        user_id (str): The user ID to get trends for
        period_type (str): The period type ("daily", "weekly", "monthly")
        num_periods (int): Number of periods to include
        
    Returns:
        List[Dict]: Energy usage trends
    """
    try:
        today = datetime.now(timezone.utc)
        
        if period_type == "daily":
            # Get daily summaries for the last specified number of days
            return await generate_daily_summaries(user_id, num_periods)
        
        elif period_type == "weekly":
            # Generate weekly summaries for past weeks
            summaries = []
            current_week_end = today - timedelta(days=today.weekday())
            current_week_end = current_week_end.replace(hour=0, minute=0, second=0, microsecond=0)
            
            for i in range(num_periods):
                end_date = current_week_end - timedelta(days=7*i)
                start_date = end_date - timedelta(days=7)
                
                summary = await generate_energy_summary(
                    user_id=user_id,
                    period="weekly",
                    start_date=start_date,
                    end_date=end_date
                )
                
                summaries.append(summary)
            
            return summaries
        
        elif period_type == "monthly":
            # Generate monthly summaries for past months
            summaries = []
            today = datetime.now(timezone.utc)
            
            for i in range(num_periods):
                # Calculate month offset
                year = today.year
                month = today.month - i
                
                # Adjust year if we go to previous year
                while month <= 0:
                    year -= 1
                    month += 12
                
                # Calculate start and end of month
                start_date = datetime(year, month, 1, tzinfo=timezone.utc)
                if month == 12:
                    end_date = datetime(year+1, 1, 1, tzinfo=timezone.utc)
                else:
                    end_date = datetime(year, month+1, 1, tzinfo=timezone.utc)
                
                summary = await generate_energy_summary(
                    user_id=user_id,
                    period="monthly",
                    start_date=start_date,
                    end_date=end_date
                )
                
                summaries.append(summary)
            
            return summaries
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid period type: {period_type}. Must be 'daily', 'weekly', or 'monthly'."
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting energy usage trends: {str(e)}"
        )

async def get_device_energy_efficiency(device_id: str, days: int = 30) -> Dict:
    """
    Calculate energy efficiency metrics for a specific device.
    
    Args:
        device_id (str): The ID of the device to analyze
        days (int): Number of days to analyze
        
    Returns:
        Dict: Energy efficiency metrics
    """
    try:
        # Get device details
        device = await get_device(device_id)
        
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get energy data for the device
        query = {
            "device_id": device_id,
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        
        energy_data = list(energy_collection.find(query).sort("timestamp", 1))
        
        if not energy_data:
            return {
                "device_id": device_id,
                "device_name": device.get("name", "Unknown Device"),
                "total_consumption": 0,
                "average_daily_consumption": 0,
                "efficiency_rating": "No data available",
                "recommendations": ["No usage data available for efficiency analysis"]
            }
        
        # Calculate metrics
        total_consumption = sum(data.get("energy_consumed", 0) for data in energy_data)
        average_daily = total_consumption / days if days > 0 else 0
        
        # Determine efficiency rating based on device type
        efficiency_rating = "Unknown"
        recommendations = []
        
        device_type = device.get("type", "").lower()
        
        if device_type == "light":
            if average_daily < 0.5:
                efficiency_rating = "Excellent"
                recommendations = ["Continue using efficient LED lighting", "Consider motion sensors for less-used areas"]
            elif average_daily < 1.0:
                efficiency_rating = "Good"
                recommendations = ["Consider upgrading to more efficient bulbs", "Reduce usage in unoccupied rooms"]
            else:
                efficiency_rating = "Poor"
                recommendations = ["Replace with LED bulbs", "Install timers or motion sensors", "Review usage patterns"]
        
        elif device_type == "thermostat":
            if average_daily < 10:
                efficiency_rating = "Excellent"
                recommendations = ["Maintain current temperature settings", "Consider smart scheduling for further optimization"]
            elif average_daily < 15:
                efficiency_rating = "Good"
                recommendations = ["Adjust temperature by 1-2 degrees to save energy", "Implement smart scheduling"]
            else:
                efficiency_rating = "Poor"
                recommendations = ["Reduce temperature variations", "Install programmable features", "Consider insulation improvements"]
        
        elif device_type == "appliance":
            if average_daily < 2:
                efficiency_rating = "Excellent"
                recommendations = ["Maintain current usage patterns", "Consider off-peak usage for further savings"]
            elif average_daily < 4:
                efficiency_rating = "Good"
                recommendations = ["Use during off-peak hours", "Consider energy-saving modes"]
            else:
                efficiency_rating = "Poor"
                recommendations = ["Consider upgrading to a more efficient model", "Reduce usage frequency", "Use eco-friendly settings"]
        
        else:
            efficiency_rating = "Unknown device type"
            recommendations = ["Register device type for tailored recommendations"]
        
        return {
            "device_id": device_id,
            "device_name": device.get("name", "Unknown Device"),
            "total_consumption": total_consumption,
            "average_daily_consumption": average_daily,
            "efficiency_rating": efficiency_rating,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating device efficiency: {str(e)}"
        )
