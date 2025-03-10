"""
This model defines user-related data models for account creation & response handling

It includes:
- `UserCreate`: A model for user registration input with email & password validation
- `UserResponse`: A model for returning user details in API responses
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

class UserCreate(BaseModel):
    '''
    Pydantic model for user registration input

    Attributes:
        email (EmailStr): The user's email address
        password (str): The user's password (validated for strength)
        role (Optional[str]): The user's role, defaulting to "user"
    '''
    email: EmailStr
    password: str
    role: Optional[str] = "user"    # Default role

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """
        Validate the password to ensure it meets security requirements

        Args:
            value (str): The password provided by the user

        Returns:
            str: The validated password

        Raises:
            ValueError: If the password doesn't meet security requirements
        """
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
        """
        Validate the user's email address

        Args:
            value (EmailStr): The email address provided

        Returns:
            EmailStr: The validated email

        Raises:
            ValueError: If the email doesn't contain `@` or a valid domain
        """
        if not "@" in value:
            raise ValueError("Email must contain @.")
        if not "." in value.split("@")[1]:
            raise ValueError("Email must contain a dot.")
        return value

class UserResponse(BaseModel):
    """
    Pydantic model for user response data

    Attributes:
        id (str): Unique identifier for the user
        role (str): The assigned role of the user
        email (EmailStr): The user's email address
        is_verified (bool): Indicates whether the user's email address is verified (defaults to False)
        created_at (Optional[datetime]): Timestamp of the user account creation
    """
    id: str
    role: str
    email: EmailStr
    is_verified: bool = False
    created_at: Optional[datetime]

    model_config = ConfigDict(from_attributes = True)
