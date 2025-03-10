from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timezone
from bson.objectid import ObjectId

from ..models.profile import Profile
from ..core.security import get_current_user, role_required
from ..db.database import profiles_collection, users_collection

router = APIRouter(
    prefix="/api/v1/profiles",
    tags=["Profiles"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", dependencies=[Depends(role_required("admin"))])
async def create_profile(profile: Profile):
    """
    Create a new user profile (admin only)
    
    Args:
        profile (Profile): The profile data to create
        
    Returns:
        dict: The created profile with ID
    
    Raises:
        HTTPException: If profile creation fails
    """
    try:
        # Verify the user exists
        user = users_collection.find_one({"_id": ObjectId(profile.user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Check if profile with same name already exists for this user
        existing_profile = profiles_collection.find_one({
            "user_id": profile.user_id,
            "name": profile.name
        })
        
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profile with this name already exists for this user"
            )
        
        # Prepare profile data
        profile_dict = profile.model_dump()
        profile_dict["created_at"] = datetime.now(timezone.utc)
        
        # Insert profile
        result = profiles_collection.insert_one(profile_dict)
        
        return {
            "message": "Profile created successfully",
            "profile_id": str(result.inserted_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}"
        )

@router.get("/", response_model=List[Profile])
async def get_profiles(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    profile_type: Optional[str] = Query(None, description="Filter by profile type"),
    current_user: dict = Depends(role_required("admin"))
):
    """
    Get all profiles with optional filtering (admin only)
    
    Args:
        user_id (Optional[str]): Filter profiles by user ID
        profile_type (Optional[str]): Filter profiles by type
        current_user (dict): The current authenticated admin user
        
    Returns:
        List[Profile]: List of profiles matching the filter criteria
    """
    query = {}
    if user_id:
        query["user_id"] = user_id
    if profile_type:
        query["profile_type"] = profile_type
        
    profiles = list(profiles_collection.find(query))
    
    # Convert ObjectId to string
    for profile in profiles:
        if '_id' in profile:
            profile['_id'] = str(profile['_id'])
            
    return profiles

@router.get("/me", response_model=List[Profile])
async def get_my_profiles(current_user: dict = Depends(get_current_user)):
    """
    Get all profiles for the current authenticated user
    
    Args:
        current_user (dict): The current authenticated user
        
    Returns:
        List[Profile]: List of profiles for the current user
    """
    # Get user ObjectId from email
    user = users_collection.find_one({"email": current_user["sub"]})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Find all profiles for this user
    user_id = str(user["_id"])
    profiles = list(profiles_collection.find({"user_id": user_id}))
    
    # Convert ObjectId to string
    for profile in profiles:
        if '_id' in profile:
            profile['_id'] = str(profile['_id'])
            
    return profiles

@router.get("/{profile_id}", response_model=Profile)
async def get_profile(profile_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get a specific profile by ID
    
    Args:
        profile_id (str): The ID of the profile to retrieve
        current_user (dict): The current authenticated user
        
    Returns:
        Profile: The requested profile
        
    Raises:
        HTTPException: If the profile is not found or user doesn't have access
    """
    try:
        # Find the profile
        profile = profiles_collection.find_one({"_id": ObjectId(profile_id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Check if admin or profile owner
        user = users_collection.find_one({"email": current_user["sub"]})
        is_admin = current_user.get("role") == "admin"
        is_owner = user and str(user["_id"]) == profile["user_id"]
        
        if not (is_admin or is_owner):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this profile"
            )
        
        # Convert ObjectId to string
        if '_id' in profile:
            profile['_id'] = str(profile['_id'])
            
        return profile
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profile: {str(e)}"
        )

@router.put("/{profile_id}", dependencies=[Depends(role_required("admin"))])
async def update_profile(profile_id: str, profile_update: Profile):
    """
    Update an existing profile (admin only)
    
    Args:
        profile_id (str): The ID of the profile to update
        profile_update (Profile): The updated profile data
        
    Returns:
        dict: Confirmation of update
        
    Raises:
        HTTPException: If the profile is not found or update fails
    """
    try:
        # Check if profile exists
        existing_profile = profiles_collection.find_one({"_id": ObjectId(profile_id)})
        if not existing_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Check if user exists
        user = users_collection.find_one({"_id": ObjectId(profile_update.user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prepare update data
        update_data = profile_update.model_dump()
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        # Update profile
        result = profiles_collection.update_one(
            {"_id": ObjectId(profile_id)},
            {"$set": update_data}
        )
        
        if result.modified_count:
            return {"message": "Profile updated successfully"}
        else:
            return {"message": "No changes applied to the profile"}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

@router.delete("/{profile_id}", dependencies=[Depends(role_required("admin"))])
async def delete_profile(profile_id: str):
    """
    Delete a profile (admin only)
    
    Args:
        profile_id (str): The ID of the profile to delete
        
    Returns:
        dict: Confirmation of deletion
        
    Raises:
        HTTPException: If the profile is not found or deletion fails
    """
    try:
        # Check if profile exists
        profile = profiles_collection.find_one({"_id": ObjectId(profile_id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Delete the profile
        result = profiles_collection.delete_one({"_id": ObjectId(profile_id)})
        
        if result.deleted_count:
            return {"message": "Profile deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete profile"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting profile: {str(e)}"
        )

@router.patch("/{profile_id}/accessibility", dependencies=[Depends(get_current_user)])
async def update_accessibility_settings(
    profile_id: str, 
    settings: dict
):
    """
    Update accessibility settings for a profile
    
    Args:
        profile_id (str): The ID of the profile to update
        settings (dict): The accessibility settings to update
        
    Returns:
        dict: Confirmation of update
        
    Raises:
        HTTPException: If the profile is not found or update fails
    """
    try:
        # Check if profile exists
        profile = profiles_collection.find_one({"_id": ObjectId(profile_id)})
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )

        # Update accessibility settings
        result = profiles_collection.update_one(
            {"_id": ObjectId(profile_id)},
            {"$set": {"accessibility_settings": settings}}
        )

        if result.modified_count:
            return {"message": "Accessibility settings updated successfully"}
        else:
            return {"message": "No changes applied to accessibility settings"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update accessibility settings: {str(e)}"
        )
