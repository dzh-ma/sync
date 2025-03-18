"""
User management routes for the smart home system with debug prints.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from datetime import datetime
from pymongo.errors import DuplicateKeyError

from app.models.user import CreateUser, UserDB, UserResponse, UserUpdate
# Import at module level for easier patching in tests
from app.db.data import u_c  # User collection
from app.core.password import hash_password, verify_role
from app.core.auth import get_current_user

# Print statement for debugging
# print("DEBUG: user_routes.py loaded, u_c object:", u_c)

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserDB = Depends(get_current_user),
    role: Optional[str] = None,
    active: Optional[bool] = None
) -> List[UserResponse]:
    """
    Get all users (admin only).
    """
    # Debug print
    # print(f"DEBUG: get_all_users called with u_c={u_c}, id(u_c)={id(u_c)}")
    
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view all users"
        )
    
    # Build query filter
    query: Dict[str, Any] = {}
    if role:
        query["role"] = role
    if active is not None:
        query["active"] = active
    
    # Debug print
    # print(f"DEBUG: Executing find with query={query}")
    
    # Convert cursor to list explicitly
    cursor = u_c.find(query).skip(skip).limit(limit)
    # print(f"DEBUG: type(cursor)={type(cursor)}, cursor={cursor}")
    
    users = list(cursor)
    # print(f"DEBUG: users={users}, len(users)={len(users)}")
    
    # Convert to UserResponse models
    return [UserResponse.model_validate(user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a single user by ID.
    Users can only access their own data, while admins can access any user's data.
    """    
    # Debug print
    # print(f"DEBUG: get_user called with user_id={user_id}, u_c={u_c}")
    
    # Check if the requesting user is the user being requested or an admin
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's data"
        )
    
    user = u_c.find_one({"id": user_id})
    # print(f"DEBUG: find_one result={user}")
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserResponse.model_validate(user)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: CreateUser,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Create a new user.
    Only admin users can create new users.
    """
    # Debug print
    # print(f"DEBUG: create_user called with username={user_create.username}, u_c={u_c}")
    
    # Verify admin role
    verify_role(current_user.role, "admin")
    
    # Check if username or email already exists
    username_exists = u_c.find_one({"username": user_create.username})
    # print(f"DEBUG: username_exists={username_exists}")
    
    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    email_exists = u_c.find_one({"email": user_create.email})
    # print(f"DEBUG: email_exists={email_exists}")
    
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Create a new UserDB model
    hashed_password = hash_password(user_create.password)
    user_db = UserDB(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password,
        role=user_create.role
    )
    
    # Insert the user into the database
    try:
        u_c.insert_one(user_db.model_dump())
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this ID, username, or email already exists"
        )
    
    return UserResponse.model_validate(user_db)

# [Add similar debug prints to other routes if needed]

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Update a user's information.
    Users can only update their own data, while admins can update any user's data.
    """
    # Check if the requesting user is the user being updated or an admin
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user's data"
        )
    
    # Find the user to update
    user = u_c.find_one({"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Create update data dictionary with only the provided fields
    update_data = {}
    if user_update.username is not None:
        # Check if new username already exists (if it's different from current)
        if user_update.username != user["username"]:
            if u_c.find_one({"username": user_update.username}):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
        update_data["username"] = user_update.username
    
    if user_update.email is not None:
        # Check if new email already exists (if it's different from current)
        if user_update.email != user["email"]:
            if u_c.find_one({"email": user_update.email}):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        update_data["email"] = user_update.email
    
    # Add updated timestamp
    update_data["updated"] = datetime.utcnow()
    
    # Perform the update if there's data to update
    if update_data:
        try:
            result = u_c.update_one(
                {"id": user_id},
                {"$set": update_data}
            )
            if result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_304_NOT_MODIFIED,
                    detail="User data not modified"
                )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update would create a duplicate username or email"
            )
    
    # Retrieve and return the updated user
    updated_user = u_c.find_one({"id": user_id})
    return UserResponse.model_validate(updated_user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: UserDB = Depends(get_current_user)
):
    """
    Delete a user.
    Only admin users can delete users.
    """
    # Verify admin role
    verify_role(current_user.role, "admin")
    
    # Find the user to delete
    user = u_c.find_one({"id": user_id})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Perform the deletion
    result = u_c.delete_one({"id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={})
