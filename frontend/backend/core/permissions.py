"""
This module defines permission-based access control for the Sync Smart Home API

It provides middleware functions to:
- Enforce profile-specific permission checks for various system features
- Gate access to APIs based on user profile capabilities
- Support the fine-grained permission system required by FR 3-1 through FR 3-4

The permission system works alongside the role-based access control in security.py,
but focuses on profile-level permissions rather than user roles. This enables more
granular control, allowing administrators to customize what actions specific profiles
can perform (controlling devices, accessing energy data, etc.).

Usage:
    from app.core.permissions import profile_permission_required
    
    @router.get("/route")
    async def protected_route(
        _ = Depends(profile_permission_required("can_access_energy_data"))
    ):
        # Only profiles with can_access_energy_data=True can access this
"""
from fastapi import Depends, HTTPException, status
from typing import Callable

from ..core.security import get_current_user
from ..db.database import profiles_collection

def profile_permission_required(permission_field: str):
    """
    Dependency function to enforce profile-specific permissions

    Args:
        permission_field (str): The profile permission field to check

    Returns:
        function: Dependency function that verifies the user's profile permissions

    Raises:
        HTTPException: If the user lacks the required permissions
    """
    def permission_checker(current_user: dict = Depends(get_current_user)):
        user_email = current_user.get("sub")
        user_profile = profiles_collection.find_one({"user_id": user_email})

        if not user_profile or not user_profile.get(permission_field, False):
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = f"Permission denied: {permission_field} required"
            )

        return current_user

    return permission_checker
