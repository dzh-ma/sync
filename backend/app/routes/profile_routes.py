"""
This module defines API routes for managing user profiles
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from app.models.profile import Profile
from app.utils.data_operations import (
    create_profile,
    get_profile,
    get_user_profiles,
    update_profile,
    delete_profile
)
from app.core.security import get_current_user, role_required

router = APIRouter(
    prefix="/api/v1/profiles",
    tags=["profiles"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def add_profile(
    profile: Profile,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new profile
    
    Args:
        profile (Profile): The profile data to create
        
    Returns:
        dict: The created profile
    """
    # In test cases, the user_id is the MongoDB ObjectId
    # Convert from sub to MongoDB ObjectId if needed
    user_id = current_user.get("sub")
    
    # Ensure the profile belongs to the currently authenticated user
    if profile.user_id != user_id and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only create profiles for your own account"
        )
        
    result = await create_profile(profile)
    return {
        "message": "Profile created successfully",
        "profile_id": str(result.get("_id"))
    }

@router.get("/me")
async def get_my_profiles(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all profiles for the current user
    
    Returns:
        list: A list of profiles for the current user
    """
    return await get_user_profiles(current_user.get("sub"))

@router.get("/{profile_id}")
async def get_profile_by_id(
    profile_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get a profile by its ID
    
    Args:
        profile_id (str): The ID of the profile to retrieve
        
    Returns:
        dict: The profile data
    """
    profile = await get_profile(profile_id)
    
    # Ensure users can only access their own profiles unless they're admin
    if profile.get("user_id") != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only access your own profiles"
        )
        
    return profile

@router.get("/")
async def get_profiles(
    profile_type: Optional[str] = Query(None, description="Filter by profile type"),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all profiles for the current user, optionally filtered by type
    
    Args:
        profile_type (Optional[str]): Filter by profile type
        
    Returns:
        list: A list of profiles
    """
    profiles = await get_user_profiles(current_user.get("sub"))
    
    # Filter by profile type if specified
    if profile_type:
        profiles = [p for p in profiles if p.get("profile_type") == profile_type]
        
    return profiles

@router.put("/{profile_id}")
async def update_profile_by_id(
    profile_id: str,
    profile_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a profile
    
    Args:
        profile_id (str): The ID of the profile to update
        profile_data (dict): The updated profile data
        
    Returns:
        dict: A success message
    """
    profile = await get_profile(profile_id)
    
    # Ensure users can only update their own profiles unless they're admin
    if profile.get("user_id") != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only update your own profiles"
        )
        
    await update_profile(profile_id, profile_data)
    return {"message": "Profile updated successfully"}

@router.patch("/{profile_id}/accessibility")
async def update_accessibility_settings(
    profile_id: str,
    settings: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a profile's accessibility settings
    
    Args:
        profile_id (str): The ID of the profile to update
        settings (dict): The accessibility settings to update
        
    Returns:
        dict: A success message
    """
    profile = await get_profile(profile_id)
    
    # Ensure users can only update their own profiles
    if profile.get("user_id") != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only update your own profiles"
        )
        
    # Update just the accessibility settings
    await update_profile(profile_id, {"accessibility_settings": settings})
    
    return {"message": "Accessibility settings updated successfully"}

@router.delete("/{profile_id}")
async def delete_profile_by_id(
    profile_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a profile
    
    Args:
        profile_id (str): The ID of the profile to delete
        
    Returns:
        dict: A success message
    """
    profile = await get_profile(profile_id)
    
    # Ensure users can only delete their own profiles unless they're admin
    if profile.get("user_id") != current_user.get("sub") and current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own profiles"
        )
        
    await delete_profile(profile_id)
    return {"message": "Profile deleted successfully"}
