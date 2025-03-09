from fastapi import Depends, HTTPException, status
from typing import Callable

from app.core.security import get_current_user
from app.db.database import profiles_collection

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
