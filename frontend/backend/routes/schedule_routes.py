"""
This module defines a FastAPI router for managing device schedules. It provides endpoints 
    to create, retrieve, and list schedules with support for filtering based on device, creator, 
    & active status.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from bson.objectid import ObjectId
from datetime import datetime, timezone

from ..models.schedule import Schedule
from ..core.security import get_current_user, role_required
from ..db.database import schedules_collection, devices_collection, users_collection

router = APIRouter(
    prefix="/api/v1/schedules",
    tags=["Schedules"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", dependencies=[Depends(get_current_user)])
async def create_schedule(schedule: Schedule):
    """
    Create a new device schedule
    
    Args:
        schedule (Schedule): The schedule data to create
        
    Returns:
        dict: The created schedule with ID
    
    Raises:
        HTTPException: If schedule creation fails
    """
    try:
        # Check if the device exists
        device = devices_collection.find_one({"id": schedule.device_id})
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found"
            )
        
        # Check if the user exists
        user = users_collection.find_one({"_id": ObjectId(schedule.created_by)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate schedule times
        if schedule.start_time >= schedule.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be before end time"
            )
            
        if schedule.start_date > schedule.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before or equal to end date"
            )
        
        # Prepare schedule data
        schedule_dict = schedule.model_dump()
        schedule_dict["created_at"] = datetime.now(timezone.utc)
        
        # Insert schedule
        result = schedules_collection.insert_one(schedule_dict)
        
        return {
            "message": "Schedule created successfully",
            "schedule_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create schedule: {str(e)}"
        ) from e

@router.get("/", response_model=List[Schedule])
async def get_schedules(
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    created_by: Optional[str] = Query(None, description="Filter by creator user ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all schedules with optional filtering
    
    Args:
        device_id (Optional[str]): Filter schedules by device
        created_by (Optional[str]): Filter schedules by creator
        is_active (Optional[bool]): Filter schedules by active status
        current_user (dict): The current authenticated user
        
    Returns:
        List[Schedule]: List of schedules matching the filter criteria
    """
    query = {}
    if device_id:
        query["device_id"] = device_id
    if created_by:
        query["created_by"] = created_by
    if is_active is not None:
        query["is_active"] = is_active
        
    schedules = list(schedules_collection.find(query))
    
    # Convert ObjectId to string for each schedule
    for schedule in schedules:
        if '_id' in schedule:
            schedule['_id'] = str(schedule['_id'])
            
    return schedules

@router.get("/{schedule_id}", response_model=Schedule)
async def get_schedule(schedule_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get a specific schedule by ID
    
    Args:
        schedule_id (str): The ID of the schedule to retrieve
        current_user (dict): The current authenticated user
        
    Returns:
        Schedule: The requested schedule
        
    Raises:
        HTTPException: If the schedule is not found
    """
    try:
        schedule = schedules_collection.find_one({"_id": ObjectId(schedule_id)})
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )
        
        # Convert ObjectId to string
        if '_id' in schedule:
            schedule['_id'] = str(schedule['_id'])
            
        return schedule
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create schedule: {str(e)}"
        ) from e
