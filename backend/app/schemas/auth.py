"""
Auth request / response Pydantic schemas.

Schemas defined here:
  RegisterRequest  — new account signup payload
  LoginRequest     — credential login payload
  RefreshRequest   — refresh token exchange payload
  LogoutRequest    — access token revocation payload
  TokenResponse    — access + refresh token pair response
  TokenData        — decoded JWT payload (internal use)
  MessageResponse  — generic success message response
"""

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Payload for POST /auth/register."""

    email: EmailStr = Field(..., description="Valid email address — used as login identifier.")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Min 8 chars, at least 1 uppercase letter and 1 digit.",
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User's display name.",
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Enforce basic password strength rules."""
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if errors:
            raise ValueError(
                f"Password must contain {' and '.join(errors)}."
            )
        return v

    @field_validator("email")
    @classmethod
    def normalise_email(cls, v: str) -> str:
        """Normalise email to lowercase."""
        return v.lower().strip()


class LoginRequest(BaseModel):
    """Payload for POST /auth/login."""

    email: EmailStr = Field(..., description="Account email address.")
    password: str = Field(..., description="Account password.")

    @field_validator("email")
    @classmethod
    def normalise_email(cls, v: str) -> str:
        return v.lower().strip()


class RefreshRequest(BaseModel):
    """Payload for POST /auth/refresh."""

    refresh_token: str = Field(..., description="A valid, non-expired refresh JWT.")


class LogoutRequest(BaseModel):
    """Payload for POST /auth/logout — carries the access token to blacklist."""

    access_token: str = Field(..., description="The access token to revoke.")


class ChangePasswordRequest(BaseModel):
    """Payload for POST /auth/change-password."""

    current_password: str = Field(..., description="The user's current password.")
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        errors = []
        if not any(c.isupper() for c in v):
            errors.append("at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            errors.append("at least one digit")
        if errors:
            raise ValueError(f"New password must contain {' and '.join(errors)}.")
        return v


# ── Response schemas ──────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """Returned on successful login or token refresh."""

    access_token: str = Field(..., description="Short-lived JWT access token.")
    refresh_token: str = Field(..., description="Long-lived JWT refresh token.")
    token_type: str = Field(default="bearer", description="Always 'bearer'.")


class TokenData(BaseModel):
    """Internal representation of a decoded JWT payload."""

    sub: str          # User UUID as string
    type: str         # "access" | "refresh"
    exp: int          # Unix timestamp
    iat: int          # Issued-at Unix timestamp
    jti: str | None = None  # Optional unique token identifier


class MessageResponse(BaseModel):
    """Generic success response for operations that don't return data."""

    message: str
