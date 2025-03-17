"""
Authentication dependencies for FastAPI.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional

from app.models.user import UserDB
from app.db.data import u_c
from app.core.password import verify_password

security = HTTPBasic()

async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserDB:
    """
    Get the currently authenticated user.
    
    Uses HTTP Basic Authentication to validate the user.
    
    Args:
        credentials: The HTTP Basic credentials from the request
        
    Returns:
        UserDB: The authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"},
    )
    
    # Try to find user by username
    user = u_c.find_one({"username": credentials.username})
    
    # If not found, try by email
    if not user:
        user = u_c.find_one({"email": credentials.username})
    
    # Check credentials
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise auth_exception
    
    # Check if user is active
    if not user.get("active", True):  # Default to active if not specified
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return UserDB(**user)
