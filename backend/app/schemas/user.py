"""
User request/response Pydantic schemas.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    """Public user representation returned by API responses."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    headline: str | None
    bio: str | None
    location: str | None
    years_of_experience: int | None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserCreate(BaseModel):
    """Fields required to create a new user in the DB (internal/CRUD use)."""
    email: EmailStr
    password: str
    full_name: str
    role: str = "user"


class UserUpdate(BaseModel):
    """Fields the user can update on their own profile."""

    full_name: str | None = Field(None, max_length=255)
    headline: str | None = Field(None, max_length=255)
    bio: str | None = Field(None, max_length=2000)
    location: str | None = Field(None, max_length=255)
    years_of_experience: int | None = Field(None, ge=0, le=60)

