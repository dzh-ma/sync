"""
Usage data management routes for the smart home system.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.models.usage import (
    CreateUsage, UsageDB, UsageResponse, UsageUpdate, 
    UsageAggregateResponse, UsageBulkCreate, UsageTimeRange
)
# Import at module level for easier patching in tests
from app.db.data import us_c, d_c  # Usage and Device collections
from app.core.auth import get_current_user
from app.models.user import UserDB  # For authorization

router = APIRouter(prefix="/usage", tags=["usage"])

def check_device_ownership(device_id: str, user_id: str) -> bool:
    """Check if a user owns a device."""
    device = d_c.find_one({"id": device_id})
    if not device:
        return False
    return device.get("user_id") == user_id

@router.get("/", response_model=List[UsageResponse])
async def get_all_usage(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserDB = Depends(get_current_user),
    device_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    status: Optional[str] = None,
    min_energy: Optional[float] = None,
    max_energy: Optional[float] = None,
    sort: Optional[str] = "timestamp_desc"  # Options: timestamp_asc, timestamp_desc, energy_asc, energy_desc
) -> List[UsageResponse]:
    """
    Get all usage records.
    Admin users can see all records, while regular users can only see records for their devices.
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return (pagination)
        current_user: The authenticated user
        device_id: Filter by device ID
        start_time: Filter by records after this time
        end_time: Filter by records before this time
        status: Filter by device status
        min_energy: Filter by minimum energy consumed
        max_energy: Filter by maximum energy consumed
        sort: Sorting method for results
        
    Returns:
        List[UsageResponse]: List of usage records
    """
    # Build query filter
    query: Dict[str, Any] = {}
    
    if device_id:
        query["device_id"] = device_id
        
        # Check device ownership for regular users
        if current_user.role != "admin":
            owns_device = check_device_ownership(device_id, current_user.id)
            if not owns_device:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to access this device's data"
                )
    elif current_user.role != "admin":
        # For non-admin users without a specific device_id, find all their devices
        user_devices = list(d_c.find({"user_id": current_user.id}))
        if not user_devices:
            return []  # User has no devices, return empty list
        
        device_ids = [device["id"] for device in user_devices]
        query["device_id"] = {"$in": device_ids}
    
    # Add time range filter if provided
    if start_time or end_time:
        time_query = {}
        if start_time:
            time_query["$gte"] = start_time
        if end_time:
            time_query["$lte"] = end_time
        if time_query:
            query["timestamp"] = time_query
    
    if status:
        query["status"] = status
    
    # Add energy consumption filter if provided
    if min_energy is not None or max_energy is not None:
        energy_query = {}
        if min_energy is not None:
            energy_query["$gte"] = min_energy
        if max_energy is not None:
            energy_query["$lte"] = max_energy
        if energy_query:
            query["energy_consumed"] = energy_query
    
    # Determine sort order
    sort_field = "timestamp"
    sort_direction = -1  # Default to newest first
    
    if sort:
        if sort == "timestamp_asc":
            sort_field, sort_direction = "timestamp", 1
        elif sort == "timestamp_desc":
            sort_field, sort_direction = "timestamp", -1
        elif sort == "energy_asc":
            sort_field, sort_direction = "energy_consumed", 1
        elif sort == "energy_desc":
            sort_field, sort_direction = "energy_consumed", -1
    
    # Convert cursor to list
    cursor = us_c.find(query).sort(sort_field, sort_direction).skip(skip).limit(limit)
    usage_records = list(cursor)
    
    # Convert to UsageResponse models
    return [UsageResponse.model_validate(record) for record in usage_records]

@router.get("/{usage_id}", response_model=UsageResponse)
async def get_usage(
    usage_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a single usage record by ID.
    Users can only access usage data for their own devices, while admins can access any record.
    
    Args:
        usage_id: The ID of the usage record to get
        current_user: The authenticated user
        
    Returns:
        UsageResponse: The requested usage record
    """
    # Get the usage record
    usage = us_c.find_one({"id": usage_id})
    
    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usage record with ID {usage_id} not found"
        )
    
    # Check device ownership for regular users
    if current_user.role != "admin":
        owns_device = check_device_ownership(usage["device_id"], current_user.id)
        if not owns_device:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this usage record"
            )
    
    return UsageResponse.model_validate(usage)

@router.post("/", response_model=UsageResponse, status_code=status.HTTP_201_CREATED)
async def create_usage(
    usage_create: CreateUsage,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create a new usage record.
    Users can only create records for their own devices, while admins can create for any device.
    
    Args:
        usage_create: Data for the new usage record
        current_user: The authenticated user
        
    Returns:
        UsageResponse: The newly created usage record
    """
    # Check device ownership for regular users
    if current_user.role != "admin":
        owns_device = check_device_ownership(usage_create.device_id, current_user.id)
        if not owns_device:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create usage data for this device"
            )
    
    # Set timestamp to now if not provided
    if not usage_create.timestamp:
        usage_create.timestamp = datetime.utcnow()
    
    # Create a new UsageDB model
    usage_db = UsageDB(**usage_create.model_dump())
    
    # Insert the usage record into the database
    try:
        us_c.insert_one(usage_db.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usage record with this ID already exists"
        )
    
    return UsageResponse.model_validate(usage_db)

@router.post("/bulk", response_model=List[UsageResponse], status_code=status.HTTP_201_CREATED)
async def create_bulk_usage(
    bulk_create: UsageBulkCreate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create multiple usage records at once.
    Users can only create records for their own devices, while admins can create for any device.
    
    Args:
        bulk_create: List of usage records to create
        current_user: The authenticated user
        
    Returns:
        List[UsageResponse]: The newly created usage records
    """
    # Check device ownership for regular users
    if current_user.role != "admin":
        for record in bulk_create.records:
            owns_device = check_device_ownership(record.device_id, current_user.id)
            if not owns_device:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not authorized to create usage data for device {record.device_id}"
                )
    
    created_records = []
    
    for record in bulk_create.records:
        # Set timestamp to now if not provided
        if not record.timestamp:
            record.timestamp = datetime.utcnow()
        
        # Create a new UsageDB model
        usage_db = UsageDB(**record.model_dump())
        
        # Insert the usage record into the database
        try:
            us_c.insert_one(usage_db.model_dump())
            created_records.append(usage_db)
        except DuplicateKeyError:
            # Continue with other records if one fails
            continue
    
    if not created_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create any usage records"
        )
    
    return [UsageResponse.model_validate(record) for record in created_records]

@router.patch("/{usage_id}", response_model=UsageResponse)
async def update_usage(
    usage_id: str,
    usage_update: UsageUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update a usage record's information.
    Users can only update records for their own devices, while admins can update any record.
    
    Args:
        usage_id: The ID of the usage record to update
        usage_update: The data to update
        current_user: The authenticated user
        
    Returns:
        UsageResponse: The updated usage record
    """
    # Find the usage record to update
    usage = us_c.find_one({"id": usage_id})
    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usage record with ID {usage_id} not found"
        )
    
    # Check device ownership for regular users
    if current_user.role != "admin":
        owns_device = check_device_ownership(usage["device_id"], current_user.id)
        if not owns_device:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this usage record"
            )
    
    # Create update data dictionary with only the provided fields
    update_data = {k: v for k, v in usage_update.model_dump().items() if v is not None}
    
    # Add updated timestamp
    update_data["updated"] = datetime.utcnow()
    
    # Perform the update if there's data to update
    if update_data:
        try:
            result = us_c.update_one(
                {"id": usage_id},
                {"$set": update_data}
            )
            if result.modified_count == 0 and len(update_data) > 1:  # > 1 to account for the updated timestamp
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED,
                    detail="Usage record data not modified"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update usage record: {str(e)}"
            )
    
    # Retrieve and return the updated usage record
    updated_usage = us_c.find_one({"id": usage_id})
    return UsageResponse.model_validate(updated_usage)

@router.delete("/{usage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usage(
    usage_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete a usage record.
    Users can only delete records for their own devices, while admins can delete any record.
    
    Args:
        usage_id: The ID of the usage record to delete
        current_user: The authenticated user
        
    Returns:
        Response: 204 No Content on success
    """
    # Find the usage record to delete
    usage = us_c.find_one({"id": usage_id})
    if not usage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usage record with ID {usage_id} not found"
        )
    
    # Check device ownership for regular users
    if current_user.role != "admin":
        owns_device = check_device_ownership(usage["device_id"], current_user.id)
        if not owns_device:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this usage record"
            )
    
    # Perform the deletion
    result = us_c.delete_one({"id": usage_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete usage record"
        )
    
    # Return a proper 204 No Content response with no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/aggregate/", response_model=UsageAggregateResponse)
async def get_usage_aggregate(
    time_range: UsageTimeRange,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get aggregated usage statistics for a specified time range and device.
    Users can only access data for their own devices, while admins can access any data.
    
    Args:
        time_range: Object containing start_time, end_time, and device_id
        current_user: The authenticated user
        
    Returns:
        UsageAggregateResponse: Aggregated usage statistics
    """
    # TimeRange validator already checks that end_time is after start_time
    
    # Check device ownership for regular users
    if current_user.role != "admin":
        if not check_device_ownership(time_range.device_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this device's data"
            )
    
    # Build query filter
    query = {
        "device_id": time_range.device_id,
        "timestamp": {
            "$gte": time_range.start_time,
            "$lte": time_range.end_time
        }
    }
    
    # Get all usage records for the specified time range and device
    cursor = us_c.find(query)
    usage_records = list(cursor)
    
    if not usage_records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No usage records found for the specified criteria"
        )
    
    # Initialize aggregation results
    total_duration = 0
    total_energy = 0
    usage_count = len(usage_records)
    
    # Collect numeric metrics for averaging
    metric_sums = {}
    metric_counts = {}
    
    for record in usage_records:
        # Sum duration and energy
        if "duration" in record and record["duration"]:
            total_duration += record["duration"]
        
        if "energy_consumed" in record and record["energy_consumed"]:
            total_energy += record["energy_consumed"]
        
        # Collect metrics for averaging
        if "metrics" in record:
            for key, value in record["metrics"].items():
                if isinstance(value, (int, float)):  # Only average numeric metrics
                    if key not in metric_sums:
                        metric_sums[key] = 0
                        metric_counts[key] = 0
                    
                    metric_sums[key] += value
                    metric_counts[key] += 1
    
    # Calculate average metrics
    average_metrics = {}
    for key in metric_sums:
        if metric_counts[key] > 0:
            average_metrics[key] = metric_sums[key] / metric_counts[key]
    
    # Create the aggregated response
    aggregated_data = UsageAggregateResponse(
        device_id=time_range.device_id,
        start_date=time_range.start_time,
        end_date=time_range.end_time,
        total_duration=total_duration,
        total_energy=total_energy,
        average_metrics=average_metrics,
        usage_count=usage_count
    )
    
    return aggregated_data
