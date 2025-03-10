"""
This module implements security features

Features include:
- Password hashing
- JWT token creation & verification
- Role-based access control
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
 
# Password hashing context
pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

# Secret key & algorithm for JWT
SECRET_KEY = "a3f9b657c1742b259b6f865f4b7e12dcf3b2a456b4f8e2dcbad678dfe1aab4e6"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt

    Args:
        password (str): The password to hash

    Returns:
        str: The hashed password

    Raises:
        ValueError: If an error occurs during hashing
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise ValueError(f"Error hashing password: {e}") from e

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against a hashed password

    Args:
        plain_password (str): The input password
        hashed_password (str): The stored hashed password
    
    Returns:
        bool: True if the password matches & False if otherwise

    Raises:
        ValueError: If an error occurs during verification
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        raise ValueError(f"Error verifying password: {e}") from e

def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a stored hashed password required rehashing

    Args:
        hashed_password (str): The existing hashed password

    Returns:
        bool: True if rehashing is required & False if otherwise
    """
    return pwd_context.needs_update(hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT token with an expiration time

    Args:
        data (dict): The payload to encode in the token
        expires_delta (Optional[timedelta], optional): The expiration time delta
            Defaults to `ACCESS_TOKEN_EXPIRE_MINUTES`

    Returns:
        str: The encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)

def verify_access_token(token: str) -> Optional[dict]:
    """
    Verify & decode a JWT access token

    Args:
        token (str): The JWT token to verify
    
    Returns:
        Optional[dict]: The decoded token payload if valid, otherwise None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        return payload
    except JWTError:
        return None

# OAuth2 authentication scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extract & validate the current user's JWT token

    Args:
        token (str): The OAuth2 token obtained from authentication

    Returns:
        dict: The decoded token payload

    Raises:
        HTTPException: If the token is invalid or missing required fields
    """
    payload = verify_access_token(token)
    if not payload or "role" not in payload:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid token")
    return payload

def role_required(required_role: str):
    """
    Dependency function to check to enforce role-based access control

    Args:
        required_role (str): The required user role

    Returns:
        function: A dependency function that verifies the user's role

    Raises:
        HTTPException: If the user lacks the required role
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = f"Permission denied: {required_role} role required"
            )
        return current_user
    return role_checker
