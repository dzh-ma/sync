"""
This module defines API routes for managing device schedules
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.models.schedule import Schedule
from app.utils.data_operations import (
    create_schedule,
    get_schedule,
    get_device_schedules,
    get_user_schedules,
    update_schedule,
    delete_schedule
)
from app.core.security import get_current_user, profile_permission_required

router = APIRouter(
    prefix="/api/v1/schedules",
    tags=["schedules"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def add_schedule(
    schedule: Schedule,
    current_user: dict = Depends(profile_permission_required("can_control_devices"))
):
    """
    Create a new schedule for a device
    
    Args:
        schedule (Schedule): The schedule to create
        
    Returns:
        dict: The created schedule
    """
    # Ensure the schedule belongs to the currently authenticated user
    if schedule.created_by != current_user.get("sub"):
        raise HTTPException(
            status_code=403,
            detail="Schedule must be created under your user ID"
        )
        
    result = await create_schedule(schedule)
    return {
        "message": "Schedule created successfully",
        "schedule_id": str(result.get("_id"))
    }

@router.get("/{schedule_id}")
async def get_schedule_by_id(
    schedule_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a schedule by its ID
    
    Args:
        schedule_id (str): The ID of the schedule to retrieve
        
    Returns:
        dict: The schedule data
    """
    schedule = await get_schedule(schedule_id)
    
    # Ensure users can only access their own schedules unless they're admin
    if schedule.get("created_by") != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only access your own schedules"
        )
        
    return schedule

@router.get("/")
async def get_schedules(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get schedules for the current user, optionally filtered by device
    
    Args:
        device_id (Optional[str]): Filter schedules by device ID
        is_active (Optional[bool]): Filter schedules by active status
        
    Returns:
        list: A list of schedules
    """
    if device_id:
        # Get schedules for a specific device
        schedules = await get_device_schedules(device_id)
        
        # Filter to only show user's own schedules unless they're admin
        if current_user.get("role") != "admin":
            schedules = [s for s in schedules if s.get("created_by") == current_user.get("sub")]
    else:
        # Get all schedules for the current user
        schedules = await get_user_schedules(current_user.get("sub"))
    
    # Apply is_active filter if specified
    if is_active is not None:
        schedules = [s for s in schedules if s.get("is_active") == is_active]
        
    return schedules

@router.put("/{schedule_id}")
async def update_schedule_by_id(
    schedule_id: str,
    schedule_data: dict,
    current_user: dict = Depends(profile_permission_required("can_control_devices"))
):
    """
    Update a schedule.
    
    Args:
        schedule_id (str): The ID of the schedule to update
        schedule_data (dict): The updated schedule data
        
    Returns:
        dict: A success message
    """
    schedule = await get_schedule(schedule_id)
    
    # Ensure users can only update their own schedules
    if schedule.get("created_by") != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only update your own schedules"
        )
        
    await update_schedule(schedule_id, schedule_data)
    return {"message": "Schedule updated successfully"}

@router.delete("/{schedule_id}")
async def delete_schedule_by_id(
    schedule_id: str,
    current_user: dict = Depends(profile_permission_required("can_control_devices"))
):
    """
    Delete a schedule
    
    Args:
        schedule_id (str): The ID of the schedule to delete
        
    Returns:
        dict: A success message
    """
    schedule = await get_schedule(schedule_id)
    
    # Ensure users can only delete their own schedules
    if schedule.get("created_by") != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own schedules"
        )
        
    await delete_schedule(schedule_id)
    return {"message": "Schedule deleted successfully"}
