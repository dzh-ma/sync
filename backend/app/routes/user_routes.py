from fastapi import APIRouter, HTTPException
from app.models.user import UserCreate, UserResponse
from app.db.database import users_collection
from app.core.security import hash_password
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered.")
    
    user_data = {
        "email": user.email,
        "password_hash": hash_password(user.password),
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    users_collection.insert_one(user_data)
    return {
        "email": user.email,
        "is_verified": False,
        "created_at": user_data["created_at"]
    }
