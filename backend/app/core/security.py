"""
JWT creation, verification, and bcrypt password hashing utilities.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# ── Password hashing ─────────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    pwd_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if plain_password matches the stored bcrypt hash."""
    pwd_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False



# ── Token helpers ─────────────────────────────────────────────────────────────
def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    """
    Internal helper — creates a signed JWT with an expiry claim and a unique JTI.

    Args:
        data: Payload dict to encode (should include 'sub').
        expires_delta: How long until this token expires.

    Returns:
        Encoded JWT string.
    """
    import uuid
    payload = data.copy()
    expire = datetime.now(tz=UTC) + expires_delta
    payload.update({
        "exp": expire,
        "iat": datetime.now(tz=UTC),
        "jti": str(uuid.uuid4()),
    })
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_access_token(subject: str | int) -> str:
    """
    Create a short-lived access token.

    Args:
        subject: Unique user identifier (e.g. user ID or email).

    Returns:
        Signed JWT access token string.
    """
    return _create_token(
        data={"sub": str(subject), "type": "access"},
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: str | int) -> str:
    """
    Create a long-lived refresh token.

    Args:
        subject: Unique user identifier.

    Returns:
        Signed JWT refresh token string.
    """
    return _create_token(
        data={"sub": str(subject), "type": "refresh"},
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT.

    Args:
        token: Raw JWT string.

    Returns:
        Decoded payload dictionary.

    Raises:
        JWTError: If the token is invalid, expired, or tampered with.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )


def get_token_subject(token: str) -> str:
    """
    Extract the subject (user ID) from a valid token.

    Args:
        token: Raw JWT string.

    Returns:
        The 'sub' claim as a string.

    Raises:
        JWTError: If decoding fails or 'sub' is missing.
    """
    payload = decode_token(token)
    sub = payload.get("sub")
    if sub is None:
        raise JWTError("Token payload missing 'sub' claim.")
    return str(sub)
