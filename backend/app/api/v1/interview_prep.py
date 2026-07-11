"""
Interview Preparation API endpoint.

POST /api/v1/interview-prep/recommendations
  - Accepts resume text
  - Calls existing rag_service.search_jobs to find top 5 matching jobs
  - Calls existing rag_service.job_match per job to get match_score + missing_skills
  - Generates interview prep content via interview_prep_service (no LLM/DB changes)
  - Returns structured InterviewPrepResponse

No existing endpoints or services are modified.
"""

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.interview_prep import InterviewPrepRequest, InterviewPrepResponse
from app.services.interview_prep_service import interview_prep_service
from app.services.rag_service import rag_service

router = APIRouter(prefix="/interview-prep", tags=["Interview Preparation"])


@router.post(
    "/recommendations",
    response_model=InterviewPrepResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate interview preparation recommendations from resume",
)
async def get_interview_prep(
    payload: InterviewPrepRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> InterviewPrepResponse:
    """
    Submit resume text to receive interview preparation cards for the top 5 matching jobs.

    For each matched job, the response includes:
    - Aptitude topics (role-based)
    - Technical topics (derived from job skills + resume gaps)
    - Communication topics (universal soft-skill set)
    - Curated practice resource links
    """
    # Step 1: Find top 5 matching jobs using existing vector search
    search_result = await rag_service.search_jobs(db, query=payload.resume_text, limit=5)

    prep_items = []
    for search_item in search_result.items:
        job = search_item.job

        # Step 2: Calculate match score + skill gaps using existing job_match logic
        match_result = await rag_service.job_match(
            db,
            resume_text=payload.resume_text,
            job_id=str(job.id),
        )

        # Step 3: Generate interview prep card (pure logic, no external calls)
        prep_item = interview_prep_service.generate(
            job=job,
            match_score=match_result.match_score,
            missing_skills=match_result.missing_skills,
        )
        prep_items.append(prep_item)

    # Sort by match score descending
    prep_items.sort(key=lambda x: x.match_score, reverse=True)

    return InterviewPrepResponse(items=prep_items)
