"""
This module defines API routes for managing smart devices
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.models.device import Device
from app.utils.data_operations import (
    create_device,
    get_device,
    get_devices,
    update_device,
    delete_device,
    get_device_energy_efficiency
)
from app.core.security import get_current_user, role_required, profile_permission_required

router = APIRouter(
    prefix="/api/v1/devices",
    tags=["devices"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def add_device(
    device: Device,
    current_user: dict = Depends(role_required("admin"))
):
    """
    Add a new device to the system (admin only)
    
    Args:
        device (Device): The device to add
        
    Returns:
        dict: The created device
    """
    result = await create_device(device)
    return {"message": "Device created successfully", "device_id": device.id}

@router.get("/{device_id}")
async def get_device_by_id(
    device_id: str,
    _ = Depends(profile_permission_required("can_control_devices"))
):
    """
    Get a device by its ID
    
    Args:
        device_id (str): The ID of the device to retrieve
        
    Returns:
        dict: The device data
    """
    return await get_device(device_id)

@router.get("/")
async def get_all_devices(
    room_id: Optional[str] = Query(None, description="Filter devices by room"),
    type: Optional[str] = Query(None, description="Filter devices by type"),
    _ = Depends(profile_permission_required("can_control_devices"))
):
    """
    Get all devices, optionally filtered by room or type
    
    Args:
        room_id (Optional[str]): The room ID to filter by
        type (Optional[str]): The device type to filter by
        
    Returns:
        list: A list of devices
    """
    devices = await get_devices(room_id)
    
    # Apply type filter if provided
    if type:
        devices = [d for d in devices if d.get("type") == type]
        
    return devices

@router.put("/{device_id}")
async def update_device_by_id(
    device_id: str,
    device_data: dict,
    current_user: dict = Depends(role_required("admin"))
):
    """
    Update a device (admin only)
    
    Args:
        device_id (str): The ID of the device to update
        device_data (dict): The updated device data
        
    Returns:
        dict: The updated device
    """
    updated = await update_device(device_id, device_data)
    return {"message": "Device updated successfully", "device": updated}

@router.post("/{device_id}/toggle")
async def toggle_device(
    device_id: str,
    _ = Depends(profile_permission_required("can_control_devices"))
):
    """
    Toggle a device's status between 'on' and 'off'
    
    Args:
        device_id (str): The ID of the device to toggle
        
    Returns:
        dict: The updated device with new status
    """
    device = await get_device(device_id)
    
    # Toggle the status
    new_status = "off" if device.get("status") == "on" else "on"
    
    # Update the device with the new status
    updated = await update_device(device_id, {"status": new_status})
    
    return {"status": new_status, "device_id": device_id}

@router.delete("/{device_id}")
async def delete_device_by_id(
    device_id: str,
    current_user: dict = Depends(role_required("admin"))
):
    """
    Delete a device (admin only)
    
    Args:
        device_id (str): The ID of the device to delete
        
    Returns:
        dict: A success message
    """
    await delete_device(device_id)
    return {"message": "Device and related data deleted successfully"}

@router.get("/{device_id}/efficiency")
async def get_device_efficiency(
    device_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    _ = Depends(profile_permission_required("can_access_energy_data"))
):
    """
    Get energy efficiency metrics for a device
    
    Args:
        device_id (str): The ID of the device to analyze
        days (int): Number of days to analyze
        
    Returns:
        dict: Energy efficiency metrics
    """
    return await get_device_energy_efficiency(device_id, days)
