"""
Profile management routes for the smart home system.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse, Response
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.models.profile import CreateProfile, ProfileDB, ProfileResponse, ProfileUpdate
# Import at module level for easier patching in tests
from app.db.data import p_c  # Profile collection
from app.core.auth import get_current_user
from app.models.user import UserDB  # For authorization

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/", response_model=List[ProfileResponse])
async def get_all_profiles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: UserDB = Depends(get_current_user),
    user_id: Optional[str] = None,
    timezone: Optional[str] = None,
    temperature_unit: Optional[str] = None,
    dark_mode: Optional[bool] = None
) -> List[ProfileResponse]:
    """
    Get all profiles.
    Admin users can see all profiles, while regular users can only see their own.
    """
    # Check if user is admin
    if current_user.role != "admin":
        # Non-admin users can only access their own profile
        user_id = current_user.id
    
    # Build query filter
    query: Dict[str, Any] = {}
    if user_id:
        query["user_id"] = user_id
    if timezone:
        query["timezone"] = timezone
    if temperature_unit:
        query["temperature_unit"] = temperature_unit
    if dark_mode is not None:
        query["dark_mode"] = dark_mode
    
    # Convert cursor to list
    cursor = p_c.find(query).skip(skip).limit(limit)
    profiles = list(cursor)
    
    # Convert to ProfileResponse models
    return [ProfileResponse.model_validate(profile) for profile in profiles]

@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a single profile by ID.
    Users can only access their own profile, while admins can access any profile.
    """
    # Get the profile
    profile = p_c.find_one({"id": profile_id})
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    # Check if the requesting user is the profile owner or an admin
    if current_user.role != "admin" and current_user.id != profile["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this profile"
        )
    
    return ProfileResponse.model_validate(profile)

@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_create: CreateProfile,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create a new profile.
    Users can only create their own profile, while admins can create any profile.
    """
    # Check if the requesting user is the profile owner or an admin
    if current_user.role != "admin" and current_user.id != profile_create.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create profile for another user"
        )
    
    # Check if a profile already exists for this user_id
    existing_profile = p_c.find_one({"user_id": profile_create.user_id})
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Profile already exists for user with ID {profile_create.user_id}"
        )
    
    # Create a new ProfileDB model
    profile_db = ProfileDB(**profile_create.model_dump())
    
    # Insert the profile into the database
    try:
        p_c.insert_one(profile_db.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile with this ID or user_id already exists"
        )
    
    return ProfileResponse.model_validate(profile_db)

@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    profile_update: ProfileUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update a profile's information.
    Users can only update their own profile, while admins can update any profile.
    """
    # Find the profile to update
    profile = p_c.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    # Check if the requesting user is the profile owner or an admin
    if current_user.role != "admin" and current_user.id != profile["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    # Create update data dictionary with only the provided fields
    update_data = {k: v for k, v in profile_update.model_dump().items() if v is not None}
    
    # Add updated timestamp
    update_data["updated"] = datetime.utcnow()
    
    # Perform the update if there's data to update
    if update_data:
        try:
            result = p_c.update_one(
                {"id": profile_id},
                {"$set": update_data}
            )
            if result.modified_count == 0 and len(update_data) > 1:  # > 1 to account for the updated timestamp
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED,
                    detail="Profile data not modified"
                )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update would create a duplicate user_id"
            )
    
    # Retrieve and return the updated profile
    updated_profile = p_c.find_one({"id": profile_id})
    return ProfileResponse.model_validate(updated_profile)

@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete a profile.
    Users can only delete their own profile, while admins can delete any profile.
    """
    # Find the profile to delete
    profile = p_c.find_one({"id": profile_id})
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    # Check if the requesting user is the profile owner or an admin
    if current_user.role != "admin" and current_user.id != profile["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this profile"
        )
    
    # Perform the deletion
    result = p_c.delete_one({"id": profile_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete profile"
        )
    
    # Return a proper 204 No Content response with no body
    return Response(status_code=status.HTTP_204_NO_CONTENT)
