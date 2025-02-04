"""This module serves to manage user data."""
# from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

class UserCreate(BaseModel):
    '''User input for account creation.'''
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Validating password against criteria to improve strength."""
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least 1 number.")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least 1 letter.")
        if not any(char.islower() for char in value):
            raise ValueError("Password must contain at least 1 lower letter.")
        if not any(char.isupper() for char in value):
            raise ValueError("Password must contain at least 1 upper letter.")
        if not any(char in '!@#$%^&*()_+-=[]{}|;\':",.<>?/' for char in value):
            raise ValueError("Password must contain at least 1 special character.")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: EmailStr) -> EmailStr:
        """Validates the email."""
        if not "@" in value:
            raise ValueError("Email must contain @.")
        if not "." in value.split("@")[1]:
            raise ValueError("Email must contain a dot.")
        return value

class UserResponse(BaseModel):
    """Response model for user account details."""
    # id: UUID
    id: str
    email: EmailStr
    is_verified: bool = False
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes = True)

