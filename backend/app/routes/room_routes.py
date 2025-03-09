"""
This module defines API routes for managing rooms within the smart home
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.models.room import Room
from app.utils.data_operations import (
    create_room,
    get_room,
    get_user_rooms,
    update_room,
    delete_room,
    aggregate_energy_data_by_room,
    get_devices
)
from app.core.security import get_current_user, role_required, profile_permission_required
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/api/v1/rooms",
    tags=["Rooms"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def add_room(
    room: Room,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new room
    
    Args:
        room (Room): The room to create
        
    Returns:
        dict: A success message with the room ID
    """
    # Ensure the room belongs to the currently authenticated user
    # The test is passing the MongoDB ObjectId as created_by
    user_id = current_user.get("sub")
    
    # Update the room's created_by if needed
    if room.created_by != user_id:
        # FIX: "None" is not assignable to "str"
        room.created_by = user_id
        
    result = await create_room(room)
    return {
        "message": "Room created successfully", 
        "room_id": room.id
    }

@router.get("/{room_id}")
async def get_room_by_id(
    room_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a room by its ID
    
    Args:
        room_id (str): The ID of the room to retrieve
        
    Returns:
        dict: The room data
    """
    room = await get_room(room_id)
    
    # Ensure users can only access their own rooms unless they're admin
    if room.get("created_by") != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only access your own rooms"
        )
        
    return room

@router.get("/")
async def get_rooms(
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all rooms for the current user, optionally filtered by creator
    
    Args:
        created_by (Optional[str]): Filter by the user who created the room
        
    Returns:
        list: A list of rooms
    """
    if created_by:
        return await get_user_rooms(created_by)
    # FIX: "None" is not assignable to "str"
    return await get_user_rooms(current_user.get("sub"))

@router.put("/{room_id}")
async def update_room_by_id(
    room_id: str,
    room_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a room

    Args:
        room_id (str): The ID of the room to update
        room_data (dict): The updated room data
        
    Returns:
        dict: A success message
    """
    room = await get_room(room_id)
    
    # Ensure users can only update their own rooms unless they're admin
    if room.get("created_by") != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only update your own rooms"
        )
        
    await update_room(room_id, room_data)
    return {"message": "Room updated successfully"}

@router.delete("/{room_id}")
async def delete_room_by_id(
    room_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a room
    
    Args:
        room_id (str): The ID of the room to delete
        
    Returns:
        dict: A success message
    """
    room = await get_room(room_id)
    
    # Ensure users can only delete their own rooms unless they're admin
    if room.get("created_by") != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own rooms"
        )
        
    await delete_room(room_id)
    return {"message": "Room deleted successfully"}

@router.get("/{room_id}/devices")
async def get_devices_in_room(
    room_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all devices in a specific room
    
    Args:
        room_id (str): The ID of the room to get devices for
        
    Returns:
        list: A list of devices in the room
    """
    # First check if the room exists and the user has access to it
    room = await get_room(room_id)
    
    # Ensure users can only access their own rooms unless they're admin
    if room.get("created_by") != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only access your own rooms"
        )
    
    # Get devices in the room
    return await get_devices(room_id)

@router.get("/energy/consumption")
async def get_energy_by_room(
    days: int = 30,
    _ = Depends(profile_permission_required("can_access_energy_data"))
):
    """
    Get energy consumption aggregated by room
    
    Args:
        days (int): Number of days to analyze
        
    Returns:
        list: Energy consumption by room
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    return await aggregate_energy_data_by_room(start_date, end_date)
