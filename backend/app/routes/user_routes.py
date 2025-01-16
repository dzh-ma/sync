"""This module routes data to the database from registration"""
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.models.user import UserCreate, UserResponse
from app.db.database import users_collection
from app.core.security import hash_password

router = APIRouter()

@router.post("/register", response_model = UserResponse)
async def register_user(user: UserCreate):
    '''Registers user to the database.'''

    # Email existance check
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code = 400, detail = "Email already registered.")

    # Data that will be collected
    user_data = {
        "email": user.email,
        "password_hash": hash_password(user.password),
        "is_verified": False,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    # Database user insert
    result = users_collection.insert_one(user_data)

    return {
        "id": str(result.inserted_id),
        "email": user.email,
        "is_verified": False,
        "created_at": user_data["created_at"]
    }
