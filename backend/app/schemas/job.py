"""
Job Pydantic schemas for request/response validation.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class JobBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    company: str = Field(..., min_length=2, max_length=255)
    location: str | None = Field(None, max_length=255)
    job_type: str | None = Field(None, description="e.g. full-time, part-time, remote, contract")
    experience_level: str | None = Field(None, description="e.g. junior, mid, senior")
    salary_min: float | None = Field(None, ge=0)
    salary_max: float | None = Field(None, ge=0)
    currency: str = Field(default="USD", max_length=10)
    description: str = Field(..., min_length=10)
    requirements: str | None = Field(None)
    benefits: str | None = Field(None)
    skills_required: list[str] | None = Field(None)
    apply_url: str | None = Field(None, max_length=1024)

    @field_validator("skills_required", mode="before")
    @classmethod
    def clean_skills(cls, v: list[str] | str | None) -> list[str] | None:
        if isinstance(v, str):
            if v.strip().startswith("[") and v.strip().endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [s.strip() for s in v.split(",") if s.strip()]
        if isinstance(v, list):
            return [s.strip() for s in v if s.strip()]
        return v


class JobCreate(JobBase):
    """Payload to create a new job."""
    pass


class JobUpdate(BaseModel):
    """Payload to update an existing job. All fields are optional."""
    title: str | None = Field(None, min_length=2, max_length=255)
    company: str | None = Field(None, min_length=2, max_length=255)
    location: str | None = Field(None, max_length=255)
    job_type: str | None = Field(None)
    experience_level: str | None = Field(None)
    salary_min: float | None = Field(None, ge=0)
    salary_max: float | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=10)
    description: str | None = Field(None, min_length=10)
    requirements: str | None = Field(None)
    benefits: str | None = Field(None)
    skills_required: list[str] | None = Field(None)
    apply_url: str | None = Field(None, max_length=1024)

    @field_validator("skills_required", mode="before")
    @classmethod
    def clean_skills(cls, v: list[str] | str | None) -> list[str] | None:
        if isinstance(v, str):
            if v.strip().startswith("[") and v.strip().endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [s.strip() for s in v.split(",") if s.strip()]
        if isinstance(v, list):
            return [s.strip() for s in v if s.strip()]
        return v


class JobOut(JobBase):
    """Job information returned by the API."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    is_indexed: bool
    is_active: bool
    posted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class JobListOut(BaseModel):
    """Paginated list response for jobs."""
    total: int
    items: list[JobOut]
    skip: int
    limit: int
