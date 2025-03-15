"""
This module defines a FastAPI router for managing smart devices and their related operations.
It provides endpoints to create, retrieve, update, delete, toggle, and control devices.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from bson.objectid import ObjectId
from datetime import datetime, timezone

from ..core.permissions import profile_permission_required
from ..models.device import Device
from ..core.security import get_current_user, role_required
from ..db.database import devices_collection, energy_collection

router = APIRouter(
    prefix="/api/v1/devices",
    tags=["Devices"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", dependencies = [Depends(role_required("admin"))])
async def create_device(device: Device):
    """
    Create a new smart device (admin only)
    
    Args:
        device (Device): The device data to create
        
    Returns:
        dict: The created device with ID
    
    Raises:
        HTTPException: If device creation fails
    """
    try:
        # Check if device with same ID already exists
        if devices_collection.find_one({"id": device.id}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device with this ID already exists"
            )

        result = devices_collection.insert_one(device.model_dump())

        return {
            "message": "Device created successfully",
            "id": str(result.inserted_id)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create device: {str(e)}"
        ) from e

@router.get("/", response_model=List[Device])
async def get_all_devices(
    room_id: Optional[str] = Query(None, description="Filter by room ID"),
    type: Optional[str] = Query(None, description="Filter by device type"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all devices with optional filtering
    
    Args:
        room_id (Optional[str]): Filter devices by room ID
        type (Optional[str]): Filter devices by type
        current_user (dict): The current authenticated user
        
    Returns:
        List[Device]: List of devices matching the filter criteria
    """
    query = {}
    if room_id:
        query["room_id"] = room_id
    if type:
        query["type"] = type

    devices = list(devices_collection.find(query))

    # Convert ObjectId to string for each device
    for device in devices:
        if '_id' in device:
            device['_id'] = str(device['_id'])

    return devices

@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get a specific device by ID
    
    Args:
        device_id (str): The ID of the device to retrieve
        current_user (dict): The current authenticated user
        
    Returns:
        Device: The requested device
        
    Raises:
        HTTPException: If the device is not found
    """
    device = devices_collection.find_one({"id": device_id})
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if '_id' in device:
        device['_id'] = str(device['_id'])

    return device

@router.put("/{device_id}", dependencies=[Depends(role_required("admin"))])
async def update_device(device_id: str, device_update: Device):
    """
    Update an existing device (admin only)
    
    Args:
        device_id (str): The ID of the device to update
        device_update (Device): The updated device data
        
    Returns:
        dict: Confirmation of update
        
    Raises:
        HTTPException: If the device is not found or update fails
    """
    existing_device = devices_collection.find_one({"id": device_id})
    if not existing_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    update_data = device_update.model_dump()
    result = devices_collection.update_one(
        {"id": device_id},
        {"$set": update_data}
    )

    if result.modified_count:
        return {"message": "Device updated successfully"}
    else:
        return {"message": "No changes applied to the device"}

@router.delete("/{device_id}", dependencies=[Depends(role_required("admin"))])
async def delete_device(device_id: str):
    """
    Delete a device (admin only)
    
    Args:
        device_id (str): The ID of the device to delete
        
    Returns:
        dict: Confirmation of deletion
        
    Raises:
        HTTPException: If the device is not found or deletion fails
    """
    device = devices_collection.find_one({"id": device_id})
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Delete the device
    result = devices_collection.delete_one({"id": device_id})

    if result.deleted_count:
        # Also delete related energy data
        energy_collection.delete_many({"device_id": device_id})
        return {"message": "Device and related data deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete device"
        )

@router.post("/{device_id}/toggle", dependencies=[Depends(get_current_user)])
async def toggle_device(device_id: str):
    """
    Toggle a device's status between "on" and "off"
    
    Args:
        device_id (str): The ID of the device to toggle
        
    Returns:
        dict: The updated device status
        
    Raises:
        HTTPException: If the device is not found or update fails
    """
    device = devices_collection.find_one({"id": device_id})
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Toggle status
    new_status = "off" if device["status"] == "on" else "on"

    result = devices_collection.update_one(
        {"id": device_id},
        {"$set": {"status": new_status}}
    )

    if result.modified_count:
        return {
            "device_id": device_id,
            "status": new_status,
            "message": f"Device {new_status}"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle device status"
        )

@router.post("/{device_id}/control")
async def control_device(
    device_id: str,
    command: dict,
    _ = Depends(profile_permission_required("can_control_devices"))
):
    """
    Control a device (requires `can_control_devices` permission)

    Args:
        device_id (str): ID of the device to control
        command (dict): Command to send to the device (e.g., {"action": "turn_on"})

    Returns:
        dict: Command result
    """
    # Get device
    device = devices_collection.find_one({"id": device_id})

    if not device:
        raise HTTPException(status_code = 404, detail = "Device not found")

    # Update device status based on command
    action = command.get("action")

    if action in ["turn_on", "turn_off"]:
        new_status = "on" if action == "turn_off" else "off"

        devices_collection.update_one(
            {"id": device_id},
            {"set": {"status": new_status}}
        )

        return {"message": f"Device {device_id} {action} successful"}
    else:
        raise HTTPException(status_code = 400, detail = "Unsupported action")
