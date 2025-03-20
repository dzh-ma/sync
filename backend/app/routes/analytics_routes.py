"""
Analytics data management routes for the smart home system.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.models.analytics import (
    AnalyticsDB, 
    AnalyticsResponse, 
    CreateAnalytics, 
    AnalyticsUpdate,
    AnalyticsQuery
)
# Import at module level for easier patching in tests
from app.db.data import an_c  # Analytics collection
from app.core.auth import get_current_user
from app.models.user import UserDB  # For authorization

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/", response_model=List[AnalyticsResponse])
async def get_all_analytics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserDB = Depends(get_current_user),
    user_id: Optional[str] = None,
    device_id: Optional[str] = None,
    data_type: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    tags: Optional[List[str]] = Query(None)
) -> List[AnalyticsResponse]:
    """
    Get all analytics data with filtering options.
    Admin users can see all analytics, while regular users can only see their own.
    """
    # Create query object and validate time range if provided
    query_params = AnalyticsQuery(
        user_id=user_id,
        device_id=device_id,
        data_type=data_type,
        start_time=start_time,
        end_time=end_time,
        tags=tags
    )
    
    if start_time and end_time:
        try:
            query_params.validate_time_range_post_init()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    # Check if user is admin
    if current_user.role != "admin":
        # Non-admin users can only access their own analytics
        query_params.user_id = current_user.id
    
    # Build MongoDB query filter
    query: Dict[str, Any] = {}
    if query_params.user_id:
        query["user_id"] = query_params.user_id
    if query_params.device_id:
        query["device_id"] = query_params.device_id
    if query_params.data_type:
        query["data_type"] = query_params.data_type
    
    # Time range filters
    if query_params.start_time or query_params.end_time:
        query["timestamp"] = {}
        if query_params.start_time:
            query["timestamp"]["$gte"] = query_params.start_time
        if query_params.end_time:
            query["timestamp"]["$lte"] = query_params.end_time
    
    # Tags filter (if one of the specified tags is in the analytics tags list)
    if query_params.tags:
        query["tags"] = {"$in": query_params.tags}
    
    # Add sorting by timestamp (descending)
    cursor = an_c.find(query).sort("timestamp", -1).skip(skip).limit(limit)
    analytics_data = list(cursor)
    
    # Convert to AnalyticsResponse models
    return [AnalyticsResponse.model_validate(item) for item in analytics_data]

@router.get("/{analytics_id}", response_model=AnalyticsResponse)
async def get_analytics(
    analytics_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a single analytics record by ID.
    Users can only access their own analytics, while admins can access any analytics.
    """
    # Get the analytics record
    analytics = an_c.find_one({"id": analytics_id})
    
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analytics with ID {analytics_id} not found"
        )
    
    # Check if the requesting user is the owner or an admin
    if current_user.role != "admin" and current_user.id != analytics["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this analytics data"
        )
    
    return AnalyticsResponse.model_validate(analytics)

@router.post("/", response_model=AnalyticsResponse, status_code=status.HTTP_201_CREATED)
async def create_analytics(
    analytics_create: CreateAnalytics,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create a new analytics record.
    Users can only create analytics for themselves, while admins can create for any user.
    """
    # Check if the requesting user is the analytics owner or an admin
    if current_user.role != "admin" and current_user.id != analytics_create.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create analytics for another user"
        )
    
    # Create a new AnalyticsDB model
    analytics_db = AnalyticsDB(**analytics_create.model_dump())
    
    # Insert the analytics into the database
    try:
        an_c.insert_one(analytics_db.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analytics with this ID already exists"
        )
    
    return AnalyticsResponse.model_validate(analytics_db)

@router.patch("/{analytics_id}", response_model=AnalyticsResponse)
async def update_analytics(
    analytics_id: str,
    analytics_update: AnalyticsUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update an analytics record.
    Users can only update their own analytics, while admins can update any analytics.
    """
    # Find the analytics to update
    analytics = an_c.find_one({"id": analytics_id})
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analytics with ID {analytics_id} not found"
        )
    
    # Check if the requesting user is the owner or an admin
    if current_user.role != "admin" and current_user.id != analytics["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this analytics data"
        )
    
    # Create update data dictionary with only the provided fields
    update_data = {k: v for k, v in analytics_update.model_dump().items() if v is not None}
    
    # Add updated timestamp
    update_data["updated"] = datetime.utcnow()
    
    # Perform the update if there's data to update
    if update_data:
        result = an_c.update_one(
            {"id": analytics_id},
            {"$set": update_data}
        )
        if result.modified_count == 0 and len(update_data) > 1:  # > 1 to account for the updated timestamp
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED,
                detail="Analytics data not modified"
            )
    
    # Retrieve and return the updated analytics
    updated_analytics = an_c.find_one({"id": analytics_id})
    return AnalyticsResponse.model_validate(updated_analytics)

@router.delete("/{analytics_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analytics(
    analytics_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete an analytics record.
    Users can only delete their own analytics, while admins can delete any analytics.
    """
    # Find the analytics to delete
    analytics = an_c.find_one({"id": analytics_id})
    if not analytics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analytics with ID {analytics_id} not found"
        )
    
    # Check if the requesting user is the owner or an admin
    if current_user.role != "admin" and current_user.id != analytics["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this analytics data"
        )
    
    # Perform the deletion
    result = an_c.delete_one({"id": analytics_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete analytics data"
        )
    
    # Return a proper 204 No Content response with no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)
