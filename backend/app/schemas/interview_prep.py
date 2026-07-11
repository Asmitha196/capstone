"""
Interview Preparation Pydantic schemas.

Defines the response structure returned by the interview prep endpoint.
No DB models involved — all fields are derived dynamically from job + resume data.
"""

from pydantic import BaseModel, Field


class PracticeLinks(BaseModel):
    """Curated practice resource links grouped by preparation category."""
    aptitude: list[str] = Field(default_factory=list)
    technical: list[str] = Field(default_factory=list)
    communication: list[str] = Field(default_factory=list)


class InterviewPrepItem(BaseModel):
    """Interview preparation card for a single matched job."""
    job_id: str
    job_title: str
    company: str
    match_score: float = Field(..., ge=0.0, le=100.0)
    missing_skills: list[str] = Field(default_factory=list)
    aptitude_topics: list[str] = Field(default_factory=list)
    technical_topics: list[str] = Field(default_factory=list)
    communication_topics: list[str] = Field(default_factory=list)
    practice_links: PracticeLinks


class InterviewPrepResponse(BaseModel):
    """Top-5 interview preparation recommendations derived from resume + job matches."""
    items: list[InterviewPrepItem]


class InterviewPrepRequest(BaseModel):
    """Request payload for generating interview preparation recommendations."""
    resume_text: str = Field(..., min_length=50, description="Plain text resume content.")
