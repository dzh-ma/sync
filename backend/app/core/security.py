"""This module implements security features."""
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

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
