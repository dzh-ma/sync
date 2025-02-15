"""This module routes data to the database from registration"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import UserCreate, UserResponse
from app.db.database import users_collection
from app.core.security import hash_password, role_required, verify_password, create_access_token, role_required

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
        "role": user.role or "user"
    }

    # Database user insert
    try:
        result = users_collection.insert_one(user_data)
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Failed to register user: {e}") from e

    return UserResponse(
        id = str(result.inserted_id),
        role = user_data["role"],
        email = user.email,
        is_verified = False,
        created_at = user_data["created_at"]
    )

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user & return a JWT token.
    """
    user = users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code = 400, detail = "Invalid username or password")

    access_token = create_access_token(
        data = {"sub": user["email"], "role": user.get("role", "user")},
        expires_delta = timedelta(minutes = 30)
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/admin/dashboard", dependencies = [Depends(role_required("admin"))])
async def get_admin_dashboard():
    return {"message": "Welcome, admin!"}
