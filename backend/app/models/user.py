"""This module serves to manage user data."""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    '''User input for account creation.'''
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(self, value: str) -> str:
        """Validating password against criteria to improve strength."""
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least 1 number.")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least 1 letter.")
        return value

class UserResponse(BaseModel):
    """Response model for user account details."""
    id: UUID
    email: EmailStr
    is_verified: bool = False
    created_at: Optional[datetime]

    class Config:
        """Pydantic configuration for UserResponse model."""
        orm_mode = True
