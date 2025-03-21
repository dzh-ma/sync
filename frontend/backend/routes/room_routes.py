"""
This module defines a FastAPI router for managing rooms and their associated devices.
It provides endpoints to create, retrieve, update, and delete rooms,
    as well as to fetch devices assigned to a specific room.

"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone

from ..models.room import Room
from ..core.security import get_current_user, role_required
from ..db.database import rooms_collection, devices_collection, users_collection

router = APIRouter(
    prefix="/api/v1/rooms",
    tags=["Rooms"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", dependencies=[Depends(get_current_user)])
async def create_room(room: Room):
    """
    Create a new room
    
    Args:
        room (Room): The room data to create
        
    Returns:
        dict: The created room with ID
    
    Raises:
        HTTPException: If room creation fails
    """
    try:
        # Check if the user exists
        user_id = room.created_by
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if room with same name already exists for this user
        existing_room = rooms_collection.find_one({
            "name": room.name,
            "created_by": room.created_by
        })
        
        if existing_room:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room with this name already exists"
            )
        
        # Prepare room data
        room_dict = room.model_dump()
        room_dict["created_at"] = datetime.now(timezone.utc)
        
        # Insert room
        result = rooms_collection.insert_one(room_dict)
        
        return {
            "message": "Room created successfully",
            "room_id": room.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create room: {str(e)}"
        )

@router.get("/", response_model=List[Room])
async def get_rooms(
    created_by: Optional[str] = Query(None, description="Filter by creator user ID"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all rooms with optional filtering
    
    Args:
        created_by (Optional[str]): Filter rooms by creator
        current_user (dict): The current authenticated user
        
    Returns:
        List[Room]: List of rooms matching the filter criteria
    """
    query = {}
    if created_by:
        query["created_by"] = created_by
        
    rooms = list(rooms_collection.find(query))
    
    # Convert ObjectId to string
    for room in rooms:
        if '_id' in room:
            room['_id'] = str(room['_id'])
            
    return rooms

@router.get("/{room_id}", response_model=Room)
async def get_room(room_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get a specific room by ID
    
    Args:
        room_id (str): The ID of the room to retrieve
        current_user (dict): The current authenticated user
        
    Returns:
        Room: The requested room
        
    Raises:
        HTTPException: If the room is not found
    """
    room = rooms_collection.find_one({"id": room_id})
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Convert ObjectId to string
    if '_id' in room:
        room['_id'] = str(room['_id'])
        
    return room

@router.put("/{room_id}", dependencies=[Depends(get_current_user)])
async def update_room(room_id: str, room_update: Room):
    """
    Update an existing room
    
    Args:
        room_id (str): The ID of the room to update
        room_update (Room): The updated room data
        
    Returns:
        dict: Confirmation of update
        
    Raises:
        HTTPException: If the room is not found or update fails
    """
    existing_room = rooms_collection.find_one({"id": room_id})
    if not existing_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Prepare update data
    update_data = room_update.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    # Update room
    result = rooms_collection.update_one(
        {"id": room_id},
        {"$set": update_data}
    )
    
    if result.modified_count:
        return {"message": "Room updated successfully"}
    else:
        return {"message": "No changes applied to the room"}

@router.delete("/{room_id}", dependencies=[Depends(get_current_user)])
async def delete_room(room_id: str):
    """
    Delete a room
    
    Args:
        room_id (str): The ID of the room to delete
        
    Returns:
        dict: Confirmation of deletion
        
    Raises:
        HTTPException: If the room is not found or deletion fails
    """
    # Check if room exists
    room = rooms_collection.find_one({"id": room_id})
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Check if there are devices in this room
    devices_in_room = devices_collection.find_one({"room_id": room_id})
    if devices_in_room:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete room with active devices. Please remove or reassign devices first."
        )
    
    # Delete the room
    result = rooms_collection.delete_one({"id": room_id})
    
    if result.deleted_count:
        return {"message": "Room deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete room"
        )

@router.get("/{room_id}/devices", dependencies=[Depends(get_current_user)])
async def get_devices_in_room(room_id: str):
    """
    Get all devices in a specific room
    
    Args:
        room_id (str): The ID of the room
        
    Returns:
        list: List of devices in the room
        
    Raises:
        HTTPException: If the room is not found
    """
    # Check if room exists
    room = rooms_collection.find_one({"id": room_id})
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    # Get devices in the room
    devices = list(devices_collection.find({"room_id": room_id}))
    
    # Convert ObjectId to string
    for device in devices:
        if '_id' in device:
            device['_id'] = str(device['_id'])
    
    return devices
