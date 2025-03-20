"""
Room management routes for the smart home system.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.models.room import CreateRoom, RoomDB, RoomResponse, RoomUpdate
# Import at module level for easier patching in tests
from app.db.data import r_c  # Room collection
from app.core.auth import get_current_user
from app.models.user import UserDB  # For authorization

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.get("/", response_model=List[RoomResponse])
async def get_all_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserDB = Depends(get_current_user),
    user_id: Optional[str] = None,
    home_id: Optional[str] = None,
    type: Optional[str] = None,
    floor: Optional[int] = None,
    active: Optional[bool] = None
) -> List[RoomResponse]:
    """
    Get all rooms with optional filtering.
    Admin users can see all rooms, while regular users can only see their own.
    """
    # Check if user is admin
    if current_user.role != "admin":
        # Non-admin users can only access their own rooms
        user_id = current_user.id
    
    # Build query filter
    query: Dict[str, Any] = {}
    if user_id:
        query["user_id"] = user_id
    if home_id:
        query["home_id"] = home_id
    if type:
        query["type"] = type
    if floor is not None:
        query["floor"] = floor
    if active is not None:
        query["active"] = active
    
    # Convert cursor to list
    cursor = r_c.find(query).skip(skip).limit(limit)
    rooms = list(cursor)
    
    # Convert to RoomResponse models
    return [RoomResponse.model_validate(room) for room in rooms]

@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a single room by ID.
    Users can only access their own rooms, while admins can access any room.
    """
    # Get the room
    room = r_c.find_one({"id": room_id})
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    
    # Check if the requesting user is the room owner or an admin
    if current_user.role != "admin" and current_user.id != room["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this room"
        )
    
    return RoomResponse.model_validate(room)

@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    room_create: CreateRoom,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create a new room.
    """
    # Create a new RoomDB model with user_id set to current user
    room_db = RoomDB(
        user_id=current_user.id,  # Set the current user as the owner
        **room_create.model_dump()
    )
    
    # Insert the room into the database
    try:
        r_c.insert_one(room_db.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Room with this ID already exists"
        )
    
    return RoomResponse.model_validate(room_db)

@router.patch("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: str,
    room_update: RoomUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update a room's information.
    Users can only update their own rooms, while admins can update any room.
    """
    # Find the room to update
    room = r_c.find_one({"id": room_id})
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    
    # Check if the requesting user is the room owner or an admin
    if current_user.role != "admin" and current_user.id != room["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this room"
        )
    
    # Create update data dictionary with only the provided fields
    update_data = {k: v for k, v in room_update.model_dump().items() if v is not None}
    
    # Add updated timestamp
    update_data["updated"] = datetime.utcnow()
    
    # Perform the update if there's data to update
    if update_data:
        try:
            result = r_c.update_one(
                {"id": room_id},
                {"$set": update_data}
            )
            if result.modified_count == 0 and len(update_data) > 1:  # > 1 to account for the updated timestamp
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED,
                    detail="Room data not modified"
                )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update would create a duplicate ID"
            )
    
    # Retrieve and return the updated room
    updated_room = r_c.find_one({"id": room_id})
    return RoomResponse.model_validate(updated_room)

@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(
    room_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete a room.
    Users can only delete their own rooms, while admins can delete any room.
    """
    # Find the room to delete
    room = r_c.find_one({"id": room_id})
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with ID {room_id} not found"
        )
    
    # Check if the requesting user is the room owner or an admin
    if current_user.role != "admin" and current_user.id != room["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this room"
        )
    
    # Perform the deletion
    result = r_c.delete_one({"id": room_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete room"
        )
    
    # Return a proper 204 No Content response with no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)
