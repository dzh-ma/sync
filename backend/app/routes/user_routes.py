"""This module routes data to the database from registration"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from app.models.user import UserCreate, UserResponse
from app.db.database import users_collection
from app.core.security import hash_password

router = APIRouter()

@router.post("/register", response_model = UserResponse)
async def register_user(user: UserCreate):
    """Registers a new user to the database."""
    # Check if email exists already
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code = 400, detail = "Registration failed, please try again.")

    # Data that will be collected
    user_data = {
        "email": user.email,
        "password_hash": hash_password(user.password),
        "is_verified": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    # Database user insert
    try:
        result = users_collection.insert_one(user_data)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Failed to register user: {e}") from e

    return UserResponse(
        id = str(result.inserted_id),
        email = user.email,
        is_verified = False,
        created_at = user_data["created_at"]
    )
