"""
Implements password security features.
"""
from passlib.context import CryptContext    # for hashing
from fastapi import HTTPException, status   # for online updating

pc = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    """
    Hashes a password.

    Args:
        p (str): Password to hash.

    Returns:
        str: Hashed password.

    Raises:
        ValueError: If password fails to hash.
    """
    try:
        return pc.hash(p)
    except Exception as e:
        raise ValueError(f"Error hashing password: {e}") from e


def verify_password(p: str, h: str) -> bool:
    """
    Matches plain-text password with the hashed password.

    Args:
        p (str): Plain-text password.
        h (str): Hashed password.

    Returns:
        bool: (True: Passwords match); (False: Passwords don't match).

    Raises:
        ValueError: If passwords fail to compare.
    """
    try:
        return pc.verify(p, h)
    except Exception as e:
        raise ValueError(f"Error verifying password: {e}") from e

def verify_role(u: str, r: str):
    """
    Enforces correct user role for access.

    Args:
        u (str): User's current role.
        r (str): Required user role.

    Raises:
        HTTPException: If user lacks the required role.
    """
    if u != r:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied. {r} role is required for access."
        )

    return True
