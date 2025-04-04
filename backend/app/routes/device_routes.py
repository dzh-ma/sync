"""
Device management routes for the smart home system.
"""
from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.models.device import CreateDevice, DeviceDB, DeviceResponse, DeviceUpdate, DeviceType, DeviceStatus
# Import at module level for easier patching in tests
from app.db.data import d_c  # Device collection
from app.core.auth import get_current_user
from app.models.user import UserDB  # For authorization

router = APIRouter(prefix="/devices", tags=["devices"])

@router.get("/", response_model=List[DeviceResponse])
async def get_all_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserDB = Depends(get_current_user),
    user_id: Optional[str] = None,
    type: Optional[DeviceType] = None,
    room_id: Optional[str] = None,
    status: Optional[DeviceStatus] = None,
    manufacturer: Optional[str] = None
) -> List[DeviceResponse]:
    """
    Get all devices.
    Admin users can see all devices, while regular users can only see their own.
    
    Filter parameters:
    - user_id: Filter by user ID
    - type: Filter by device type
    - room_id: Filter by room ID
    - status: Filter by device status
    - manufacturer: Filter by manufacturer
    """
    # Check if user is admin
    if current_user.role != "admin":
        # Non-admin users can only access their own devices
        user_id = current_user.id
    
    # Build query filter
    query: Dict[str, Any] = {}
    if user_id:
        query["user_id"] = user_id
    if type:
        query["type"] = type
    if room_id:
        query["room_id"] = room_id
    if status:
        query["status"] = status
    if manufacturer:
        query["manufacturer"] = manufacturer
    
    # Convert cursor to list
    cursor = d_c.find(query).skip(skip).limit(limit)
    devices = list(cursor)
    
    # Convert to DeviceResponse models
    return [DeviceResponse.model_validate(device) for device in devices]

@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a single device by ID.
    Users can only access their own devices, while admins can access any device.
    """
    # Get the device
    device = d_c.find_one({"id": device_id})
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    # Check if the requesting user is the device owner or an admin
    if current_user.role != "admin" and current_user.id != device["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this device"
        )
    
    return DeviceResponse.model_validate(device)

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_create: CreateDevice,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create a new device.
    Users can only create devices for themselves, while admins can create devices for any user.
    """
    # Check if the requesting user is the device owner or an admin
    if current_user.role != "admin" and current_user.id != device_create.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create device for another user"
        )
    
    # Generate a unique ID for the device
    device_id = str(uuid.uuid4())
    
    # Create a new DeviceDB model with the generated ID
    device_data = device_create.model_dump()
    device_data["id"] = device_id
    device_db = DeviceDB(**device_data)
    
    # Insert the device into the database
    try:
        d_c.insert_one(device_db.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this ID already exists"
        )
    
    # Fetch the newly created device from the database
    device = d_c.find_one({"id": device_id})
    
    return DeviceResponse.model_validate(device)

@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_update: DeviceUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update a device's information.
    Users can only update their own devices, while admins can update any device.
    """
    # Find the device to update
    device = d_c.find_one({"id": device_id})
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    # Check if the requesting user is the device owner or an admin
    if current_user.role != "admin" and current_user.id != device["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this device"
        )
    
    # Create update data dictionary with only the provided fields
    update_data = {k: v for k, v in device_update.model_dump().items() if v is not None}
    
    # Add updated timestamp
    update_data["updated"] = datetime.utcnow()
    
    # Perform the update if there's data to update
    if update_data:
        try:
            result = d_c.update_one(
                {"id": device_id},
                {"$set": update_data}
            )
            if result.modified_count == 0 and len(update_data) > 1:  # > 1 to account for the updated timestamp
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED,
                    detail="Device data not modified"
                )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update would create a duplicate device"
            )
    
    # Retrieve and return the updated device
    updated_device = d_c.find_one({"id": device_id})
    return DeviceResponse.model_validate(updated_device)

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete a device.
    Users can only delete their own devices, while admins can delete any device.
    """
    # Find the device to delete
    device = d_c.find_one({"id": device_id})
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    # Check if the requesting user is the device owner or an admin
    if current_user.role != "admin" and current_user.id != device["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this device"
        )
    
    # Perform the deletion
    result = d_c.delete_one({"id": device_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete device"
        )
    
    # Return a proper 204 No Content response with no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)
