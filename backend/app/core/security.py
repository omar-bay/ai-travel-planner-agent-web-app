from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union
from jose import jwt
from passlib.hash import argon2
from .config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its Argon2 hash.
    Returns True if the password matches.
    """
    try:
        return argon2.verify(plain_password, hashed_password)
    except Exception:
        # If the hash is invalid or corrupted, verification fails safely
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password securely using Argon2.
    Argon2 automatically handles salting and parameter management.
    """
    return argon2.hash(password)


def create_access_token(
    subject: Union[str, int],
    expires_minutes: Optional[int] = None
) -> str:
    """
    Create a signed JWT access token with an expiration.
    """
    expires_delta = timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    expire = datetime.now(timezone.utc) + expires_delta

    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt
