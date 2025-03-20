"""
Notification management routes for the smart home system.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.models.notification import (
    CreateNotification, 
    NotificationDB, 
    NotificationResponse, 
    NotificationUpdate,
    NotificationBulkUpdate
)
# Import at module level for easier patching in tests
from app.db.data import n_c  # Notification collection
from app.core.auth import get_current_user
from app.models.user import UserDB  # For authorization

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_all_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserDB = Depends(get_current_user),
    user_id: Optional[str] = None,
    read: Optional[bool] = None,
    type: Optional[str] = None,
    priority: Optional[str] = None,
    source: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> List[NotificationResponse]:
    """
    Get all notifications.
    Admin users can see all notifications, while regular users can only see their own.
    """
    # Check if user is admin
    if current_user.role != "admin":
        # Non-admin users can only access their own notifications
        user_id = current_user.id
    
    # Build query filter
    query: Dict[str, Any] = {}
    if user_id:
        query["user_id"] = user_id
    if read is not None:
        query["read"] = read
    if type:
        query["type"] = type
    if priority:
        query["priority"] = priority
    if source:
        query["source"] = source
    
    # Date range query
    date_query = {}
    if from_date:
        date_query["$gte"] = from_date
    if to_date:
        date_query["$lte"] = to_date
    if date_query:
        query["timestamp"] = date_query
    
    # Convert cursor to list
    cursor = n_c.find(query).sort("timestamp", -1).skip(skip).limit(limit)
    notifications = list(cursor)
    
    # Convert to NotificationResponse models
    return [NotificationResponse.model_validate(notification) for notification in notifications]

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a single notification by ID.
    Users can only access their own notifications, while admins can access any notification.
    """
    # Get the notification
    notification = n_c.find_one({"id": notification_id})
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    
    # Check if the requesting user is the notification owner or an admin
    if current_user.role != "admin" and current_user.id != notification["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this notification"
        )
    
    return NotificationResponse.model_validate(notification)

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_create: CreateNotification,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create a new notification.
    Admins can create notifications for any user,
    regular users can only create notifications for themselves.
    """
    # Check if the requesting user is the notification owner or an admin
    if current_user.role != "admin" and current_user.id != notification_create.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create notification for another user"
        )
    
    # Create a new NotificationDB model
    notification_db = NotificationDB(**notification_create.model_dump())
    
    # Insert the notification into the database
    try:
        n_c.insert_one(notification_db.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notification with this ID already exists"
        )
    
    return NotificationResponse.model_validate(notification_db)

@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: str,
    notification_update: NotificationUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update a notification's information.
    Users can only update their own notifications, while admins can update any notification.
    """
    # Find the notification to update
    notification = n_c.find_one({"id": notification_id})
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    
    # Check if the requesting user is the notification owner or an admin
    if current_user.role != "admin" and current_user.id != notification["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this notification"
        )
    
    # Create update data dictionary with only the provided fields
    update_data = {k: v for k, v in notification_update.model_dump().items() if v is not None}
    
    # If marking as read, add the read timestamp
    if notification_update.read is True and notification.get("read") is False:
        update_data["read_timestamp"] = datetime.utcnow()
    
    # If marking as unread, remove the read timestamp
    if notification_update.read is False:
        update_data["read_timestamp"] = None
    
    # Perform the update if there's data to update
    if update_data:
        try:
            result = n_c.update_one(
                {"id": notification_id},
                {"$set": update_data}
            )
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED,
                    detail="Notification data not modified"
                )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update would create a duplicate notification ID"
            )
    
    # Retrieve and return the updated notification
    updated_notification = n_c.find_one({"id": notification_id})
    return NotificationResponse.model_validate(updated_notification)

@router.post("/bulk_update", response_model=dict)
async def bulk_update_notifications(
    bulk_update: NotificationBulkUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update multiple notifications at once (typically to mark them as read/unread).
    Users can only update their own notifications, while admins can update any notification.
    """
    # Build query to match only authorized notifications
    query = {
        "id": {"$in": bulk_update.notification_ids}
    }
    
    # For regular users, restrict to their own notifications
    if current_user.role != "admin":
        query["user_id"] = current_user.id
    
    # Set up update data
    update_data = {"read": bulk_update.read}
    if bulk_update.read:
        update_data["read_timestamp"] = datetime.utcnow()
    else:
        update_data["read_timestamp"] = None
    
    # Perform the update
    result = n_c.update_many(
        query,
        {"$set": update_data}
    )
    
    return {
        "modified_count": result.modified_count,
        "matched_count": result.matched_count
    }

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete a notification.
    Users can only delete their own notifications, while admins can delete any notification.
    """
    # Find the notification to delete
    notification = n_c.find_one({"id": notification_id})
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    
    # Check if the requesting user is the notification owner or an admin
    if current_user.role != "admin" and current_user.id != notification["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this notification"
        )
    
    # Perform the deletion
    result = n_c.delete_one({"id": notification_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )
    
    # Return a proper 204 No Content response with no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notifications(
    current_user: UserDB = Depends(get_current_user),
    user_id: Optional[str] = None,
    read: Optional[bool] = None,
    type: Optional[str] = None,
    priority: Optional[str] = None,
    source: Optional[str] = None
):
    """
    Delete multiple notifications based on filter criteria.
    Users can only delete their own notifications, while admins can delete any notification.
    """
    # Build query
    query = {}
    
    # Check if user is admin
    if current_user.role != "admin":
        # Non-admin users can only delete their own notifications
        query["user_id"] = current_user.id
    elif user_id:
        # Admin users can specify a user_id filter
        query["user_id"] = user_id
    
    # Add additional filters if provided
    if read is not None:
        query["read"] = read
    if type:
        query["type"] = type
    if priority:
        query["priority"] = priority
    if source:
        query["source"] = source
    
    # Perform the deletion
    result = n_c.delete_many(query)
    
    # Return a proper 204 No Content response with no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)
