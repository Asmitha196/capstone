"""
Resume analysis API endpoints.
"""

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.resume_analysis import ResumeAnalysisRequest, ResumeAnalysisResponse
from app.services.resume_analysis_service import resume_analysis_service

router = APIRouter(prefix="/resume", tags=["Resume Analysis"])


@router.post(
    "/analyze",
    response_model=ResumeAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze resume text and extract matching insights",
)
async def analyze_resume(
    payload: ResumeAnalysisRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> ResumeAnalysisResponse:
    """
    Submit resume text along with optional target job title and target job description
    to parse skills, summarize experience, identify missing skills, and get optimization recommendations.
    Requires caller to be authenticated.
    """
    return await resume_analysis_service.analyze_resume(payload)
