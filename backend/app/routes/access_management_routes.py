"""
Access management routes for the smart home system.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.models.access_management import (
    CreateAccessManagement, 
    AccessManagementDB, 
    AccessManagementResponse, 
    AccessManagementUpdate,
    ResourceType,
    AccessLevel
)
# Import at module level for easier patching in tests
from app.db.data import am_c  # Access Management collection
from app.core.auth import get_current_user
from app.models.user import UserDB  # For authorization

router = APIRouter(prefix="/access-management", tags=["access-management"])

@router.get("/", response_model=List[AccessManagementResponse])
async def get_all_access_management(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserDB = Depends(get_current_user),
    owner_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    resource_type: Optional[ResourceType] = None,
    user_id: Optional[str] = None,
    access_level: Optional[AccessLevel] = None,
    active: Optional[bool] = None
) -> List[AccessManagementResponse]:
    """
    Get all access management entries.
    
    Admin users can see all entries.
    Regular users can only see entries where they are the owner or the granted user.
    """
    # Build query filter
    query: Dict[str, Any] = {}
    
    # Check if user is admin
    if current_user.role != "admin":
        # Non-admin users can only access entries they own or are granted to them
        query["$or"] = [
            {"owner_id": current_user.id},
            {"user_id": current_user.id}
        ]
    
    # Add filters if provided
    if owner_id:
        query["owner_id"] = owner_id
    if resource_id:
        query["resource_id"] = resource_id
    if resource_type:
        query["resource_type"] = resource_type
    if user_id:
        query["user_id"] = user_id
    if access_level:
        query["access_level"] = access_level
    if active is not None:
        query["active"] = active
    
    # Convert cursor to list
    cursor = am_c.find(query).skip(skip).limit(limit)
    entries = list(cursor)
    
    # Convert to AccessManagementResponse models
    return [AccessManagementResponse.model_validate(entry) for entry in entries]

@router.get("/{entry_id}", response_model=AccessManagementResponse)
async def get_access_management(
    entry_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a single access management entry by ID.
    
    Users can only access entries where they are the owner or the granted user.
    Admin users can access any entry.
    """
    # Get the entry
    entry = am_c.find_one({"id": entry_id})
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Access management entry with ID {entry_id} not found"
        )
    
    # Check if the requesting user is the owner, the granted user, or an admin
    if (current_user.role != "admin" and 
        current_user.id != entry["owner_id"] and 
        current_user.id != entry["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this entry"
        )
    
    return AccessManagementResponse.model_validate(entry)

@router.post("/", response_model=List[AccessManagementResponse], status_code=status.HTTP_201_CREATED)
async def create_access_management(
    access_create: CreateAccessManagement,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create new access management entries.
    
    Users can only create entries where they are the owner.
    Admin users can create entries for any owner.
    """
    # Check if the requesting user is the owner or an admin
    if current_user.role != "admin" and current_user.id != access_create.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create access for another owner"
        )
    
    # Create a list to hold all created entries
    created_entries = []
    
    # Create an entry for each user_id in the list
    for user_id in access_create.user_ids:
        # Create a new AccessManagementDB model
        access_db = AccessManagementDB(
            owner_id=access_create.owner_id,
            resource_id=access_create.resource_id,
            resource_type=access_create.resource_type,
            user_id=user_id,
            access_level=access_create.access_level,
            expires_at=access_create.expires_at,
            note=access_create.note
        )
        
        # Insert the entry into the database
        try:
            am_c.insert_one(access_db.model_dump())
            created_entries.append(access_db)
        except DuplicateKeyError:
            # Skip duplicates and continue
            continue
    
    if not created_entries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access entries were created. They might already exist."
        )
    
    return [AccessManagementResponse.model_validate(entry) for entry in created_entries]

@router.patch("/{entry_id}", response_model=AccessManagementResponse)
async def update_access_management(
    entry_id: str,
    access_update: AccessManagementUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update an access management entry.
    
    Users can only update entries where they are the owner.
    Admin users can update any entry.
    """
    # Find the entry to update
    entry = am_c.find_one({"id": entry_id})
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Access management entry with ID {entry_id} not found"
        )
    
    # Check if the requesting user is the owner or an admin
    if current_user.role != "admin" and current_user.id != entry["owner_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this access entry"
        )
    
    # Create update data dictionary with only the provided fields
    update_data = {k: v for k, v in access_update.model_dump().items() if v is not None}
    
    # Add updated timestamp
    update_data["updated"] = datetime.utcnow()
    
    # Perform the update if there's data to update
    if update_data:
        try:
            result = am_c.update_one(
                {"id": entry_id},
                {"$set": update_data}
            )
            if result.modified_count == 0 and len(update_data) > 1:  # > 1 to account for the updated timestamp
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED,
                    detail="Access management entry not modified"
                )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update would create a duplicate entry"
            )
    
    # Retrieve and return the updated entry
    updated_entry = am_c.find_one({"id": entry_id})
    return AccessManagementResponse.model_validate(updated_entry)

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_access_management(
    entry_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete an access management entry.
    
    Users can only delete entries where they are the owner.
    Admin users can delete any entry.
    """
    # Find the entry to delete
    entry = am_c.find_one({"id": entry_id})
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Access management entry with ID {entry_id} not found"
        )
    
    # Check if the requesting user is the owner or an admin
    if current_user.role != "admin" and current_user.id != entry["owner_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this access entry"
        )
    
    # Perform the deletion
    result = am_c.delete_one({"id": entry_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete access management entry"
        )
    
    # Return a proper 204 No Content response with no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)
