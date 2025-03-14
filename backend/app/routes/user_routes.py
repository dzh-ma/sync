"""
This module defines user-related API routes for registration, authentication & role-based access

It includes:
- User registration with hashed password storage
- User authentication & JWT token issuance
- Admin dashboard access (restricted to users with the "admin" role)
"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from starlette.types import HTTPExceptionHandler
from app.models.user import UserCreate, UserResponse
from app.db.database import users_collection
from app.core.security import hash_password, role_required, verify_password, create_access_token
from app.utils.email_verification import generate_verification_token, send_verification_email, confirm_verification_token

router = APIRouter()

@router.post("/register", response_model = UserResponse)
async def register_user(user: UserCreate, background_tasks: BackgroundTasks):
    """
    Register a new user in the database

    Args:
        user (UserCreate): User registration data including email, password & optional role

    Returns:
        UserResponse: The created user information excluding password

    Raises:
        HTTPException (400): If the email is already registered
        HTTPException (500): If there is an error inserted the user into the database
    """
    # Check if email exists already
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code = 400, detail = "Registration failed, please try again.")

    # Prepare user data for insertion
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
    except Exception as exc:
        raise HTTPException(status_code = 500, detail = f"Failed to register user: {exc}") from exc

    # Generate verification token & schedule when verification email sends
    token = generate_verification_token(user.email)
    background_tasks.add_task(send_verification_email, user.email, token)

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
    Authenticate user & return a JWT token

    Args:
        form_data (OAuth2PasswordRequestForm): User-provided login credentials

    Returns:
        dict: A dictionary containing the access token & token type

    Raises:
        HTTPException (400): If the username or password is incorrect
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
    """
    Admin dashboard  endpoint (restricted access)

    Returns:
        dict: A welcome message confirming admin access
    """
    return {"message": "Welcome, admin!"}

@router.get("/verify")
async def verify_email(token: str):
    # Decode & verify the token to retrieve the email
    email = confirm_verification_token(token)

    # Update the user's record to set is_verified to True
    result = users_collection.update_one({"email": email}, {"$set": {"is_verified": True}})
    if result.modified_count == 0:
        raise HTTPException(status_code = 400, detail = "User couldn't be verified.")

    return {"message": "Email verified successfully."}
