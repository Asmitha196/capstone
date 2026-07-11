"""
Resume analysis Pydantic schemas.
"""

from pydantic import BaseModel, Field


class ResumeAnalysisRequest(BaseModel):
    """Payload to request resume analysis."""
    resume_text: str = Field(..., min_length=50, description="The plain text content extracted from a resume.")
    target_job_title: str | None = Field(None, max_length=255, description="Desired job title to compare against.")
    target_job_description: str | None = Field(None, description="Job description or requirements to identify missing skills.")


class ResumeAnalysisResponse(BaseModel):
    """Structured response from the resume analysis pipeline."""
    extracted_skills: list[str] = Field(..., description="Skills identified in the resume.")
    experience: str = Field(..., description="Summary of work experience, roles, and duration.")
    missing_skills: list[str] = Field(..., description="Skills recommended for the target role that are missing in the resume.")
    recommendations: list[str] = Field(..., description="Actionable recommendations to improve the resume or profile.")
