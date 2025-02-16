"""This module implements security features."""
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
    """This method hashes plain-text passwords using bcrypt."""
    try:
        return pwd_context.hash(password)
    except Exception as e:
        raise ValueError(f"Error hashing password: {e}") from e

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """This method verifies a plain-text password against a hashed password."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        raise ValueError(f"Error verifying password: {e}") from e

def needs_rehash(hashed_password: str) -> bool:
    """Check if the hashed password needs rehashing."""
    return pwd_context.needs_update(hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT token with expiration.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)

def verify_access_token(token: str) -> Optional[dict]:
    """
    Verify a JWT token & return the decoded payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms = [ALGORITHM])
        return payload
    except JWTError:
        return None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decode & validate the current user's token.
    """
    payload = verify_access_token(token)
    if not payload or "role" not in payload:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Invalid token")
    return payload

def role_required(required_role: str):
    """
    Dependency to check if the user has the required role.
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail = f"Permission denied: {required_role} role required"
            )
        return current_user
    return role_checker
