"""
RAG request/response Pydantic schemas.
"""

from pydantic import BaseModel, Field

from app.schemas.job import JobOut


class RagSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    limit: int = Field(default=5, ge=1, le=50)


class RagSearchResponseItem(BaseModel):
    job: JobOut
    score: float = Field(..., description="Cosine similarity score (0.0 to 1.0).")


class RagSearchResponse(BaseModel):
    items: list[RagSearchResponseItem]


class RagAskRequest(BaseModel):
    question: str = Field(..., min_length=3)


class RagAskResponse(BaseModel):
    answer: str
    context_jobs: list[JobOut]


class RagAnalyseResumeRequest(BaseModel):
    resume_text: str = Field(..., min_length=50)


class RagJobMatchRequest(BaseModel):
    resume_text: str = Field(..., min_length=50)
    job_id: str = Field(..., description="UUID of the job listing to match against.")


class RagJobMatchResponse(BaseModel):
    match_score: float = Field(..., ge=0.0, le=100.0, description="Match score index.")
    matching_skills: list[str]
    missing_skills: list[str]
    explanation: str


class RagEmbedJobsResponse(BaseModel):
    message: str
    jobs_embedded: int
