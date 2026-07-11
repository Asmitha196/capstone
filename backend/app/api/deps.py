"""
Shared FastAPI dependencies injected into route handlers.
Covers: DB session, current user resolution, role-based access control.
"""

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CredentialsException, ForbiddenException, TokenExpiredException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.token_blacklist import TokenBlacklist
from app.models.user import User

# ── Auth scheme ───────────────────────────────────────────────────────────────
bearer_scheme = HTTPBearer(auto_error=False)

# ── Type aliases ─────────────────────────────────────────────────────────────
DBSession = Annotated[AsyncSession, Depends(get_db)]
BearerToken = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)]


# ── Token extraction helper ───────────────────────────────────────────────────
async def _get_user_from_token(
    credentials: BearerToken,
    db: DBSession,
) -> User:
    """
    Validate a Bearer JWT and return the associated User.
    Checks token signature, expiry, type claim, blacklist, and user existence.
    """
    if credentials is None:
        raise CredentialsException("Authorization header missing.")

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except JWTError as exc:
        if "expired" in str(exc).lower():
            raise TokenExpiredException() from exc
        raise CredentialsException(str(exc)) from exc

    # Ensure this is an access token (not a refresh token)
    if payload.get("type") != "access":
        raise CredentialsException("Invalid token type. Use an access token.")

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise CredentialsException("Token payload is missing 'sub' claim.")

    jti: str | None = payload.get("jti")
    # Check blacklist if jti is present
    if jti:
        result = await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        )
        if result.scalar_one_or_none():
            raise CredentialsException("Token has been revoked.")

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError as exc:
        raise CredentialsException("Invalid user identifier in token.") from exc

    # Load user from DB
    result = await db.execute(select(User).where(User.id == user_uuid))
    user: User | None = result.scalar_one_or_none()

    if user is None:
        raise CredentialsException("User not found.")
    if not user.is_active:
        raise CredentialsException("User account is inactive.")

    return user


# ── Public dependencies ───────────────────────────────────────────────────────
async def get_current_user(
    credentials: BearerToken,
    db: DBSession,
) -> User:
    """Dependency: resolve and return the authenticated User."""
    return await _get_user_from_token(credentials, db)


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Dependency: ensure the resolved user is active."""
    if not current_user.is_active:
        raise CredentialsException("Inactive user.")
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """Dependency: ensure the resolved user has the admin role."""
    if current_user.role != "admin":
        raise ForbiddenException("Admin privileges required.")
    return current_user


# ── Convenient type aliases for route signatures ──────────────────────────────
CurrentUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(get_current_admin_user)]
