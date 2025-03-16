"""
Models for user validation.
"""
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class CreateUser(BaseModel):
    """
    Model for user registration input.

    Attributes:
        username (str): User's desired username.
        email (str): User's email address.
        password (str): User's password.
    """
    username: str
    email: EmailStr
    password: str
    role: str = "admin"     # Defaults to admin

    @field_validator("username")
    @classmethod
    def validate_username(cls, u: str) -> str:
        """
        Validate username according to requirements.

        Arguments:
            u (str): Username to be validated.

        Returns:
            str: Validated username.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if len(u) > 3:
            raise ValueError("Username must be at least 3 characters long.")
        if len(u) < 30:
            raise ValueError("Username must be less than 30 characters long.")

        return u

    @field_validator("password")
    @classmethod
    def validate_password(cls, p: str) -> str:
        """
        Validate password according to requirements.

        Arguments:
            p (str): Password to be validated.

        Returns:
            str: Validated password.

        Raises:
            ValueError: Validation encountered a missing requirement.
        """
        if len(p) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not any(c.isdigit() for c in p):
            raise ValueError("Password must contain at least 1 number.")
        if not any(c.isalpha() for c in p):
            raise ValueError("Password must contain at least 1 letter.")
        if not any(c.islower() for c in p):
            raise ValueError("Password must contain at least 1 lowercase letter.")
        if not any(c.isupper() for c in p):
            raise ValueError("Password must contain at least 1 uppercase letter.")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",.<>?/" for c in p):
            raise ValueError("Password must contain at least 1 special character.")

        return p


# What gets stored in MongoDB
class UserDB(BaseModel):
    """
    Internal model representing user data in the database.

    Attributes:
        id (str): Unique user identifier.
        username (str): Username.
        email (EmailStr): User's email address.
        hashed_password (str): Securely hashed password.
        active (bool): Whether the user account is currently active.
        created (datetime): When the user account was created.
        updated (Optional[datetime]): When the user account was last updated.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
