"""
This module provides functionality for profile-based permission checks

Usage:
    from app.core.permissions import profile_permission_required
    
    @router.get("/route")
    async def protected_route(
        _ = Depends(profile_permission_required("can_access_energy_data"))
    ):
        # Only profiles with can_access_energy_data=True can access this
"""
from typing import Optional
from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user, oauth2_scheme
from app.db.database import profiles_collection

async def get_user_active_profile(current_user: dict) -> Optional[dict]:
    """
    Get the active profile for the current user
    
    Args:
        current_user (dict): The current authenticated user
        
    Returns:
        Optional[dict]: The active profile if one exists, otherwise None
    """
    active_profile = profiles_collection.find_one({
        "user_id": current_user.get("sub"),
        "is_active": True
    })
    
    return active_profile

def profile_permission_required(permission: str):
    """
    Dependency function to enforce profile-specific permissions

    Args:
        permission_field (str): The profile permission field to check

    Returns:
        function: Dependency function that verifies the user's profile permissions

    Raises:
        HTTPException: If the user lacks the required permissions
    """
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        # Admin users always have all permissions
        if current_user.get("role") == "admin":
            return current_user

        # Get the active profile for this user
        active_profile = await get_user_active_profile(current_user)

        if not active_profile:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "No active profile found. Please set an active profile."
            )
            
        # Check if the profile has the required permission
        if not active_profile.get(permission, False):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = "Your current profile does not have permission to perform this action."
            )

        return current_user

    return permission_checker

