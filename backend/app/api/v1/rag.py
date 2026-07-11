"""
RAG API endpoints.
Provides vector search, ask-context QA, resume analysis, job matching, and embedding trigger operations.
"""

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.rag import (
    RagAnalyseResumeRequest,
    RagAskRequest,
    RagAskResponse,
    RagEmbedJobsResponse,
    RagJobMatchRequest,
    RagJobMatchResponse,
    RagSearchRequest,
    RagSearchResponse,
)
from app.schemas.resume_analysis import ResumeAnalysisResponse
from app.services.rag_service import rag_service

router = APIRouter(prefix="/rag", tags=["RAG Module"])


@router.post(
    "/search",
    response_model=RagSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Vector similarity search for jobs",
)
async def search_jobs(
    payload: RagSearchRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> RagSearchResponse:
    """
    Search active job postings using vector similarity embeddings.
    """
    return await rag_service.search_jobs(db, query=payload.query, limit=payload.limit)


@router.post(
    "/ask",
    response_model=RagAskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask questions using jobs context",
)
async def ask(
    payload: RagAskRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> RagAskResponse:
    """
    Submit a career or job-related query. Retrieves relevant listings and uses them
    as context to answer the question using Groq LLM.
    """
    return await rag_service.ask(db, question=payload.question)


@router.post(
    "/analyse-resume",
    response_model=ResumeAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="RAG-based resume analysis",
)
async def analyse_resume(
    payload: RagAnalyseResumeRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> ResumeAnalysisResponse:
    """
    Submit a resume. Matches the resume content against active job postings in the database,
    returning extracted skills, experience summary, and specific skills gaps relative to matched listings.
    """
    return await rag_service.analyze_resume_rag(db, resume_text=payload.resume_text)


@router.post(
    "/job-match",
    response_model=RagJobMatchResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate resume match score against a job",
)
async def job_match(
    payload: RagJobMatchRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> RagJobMatchResponse:
    """
    Compares resume text directly with a specific job database entry, scoring the alignment
    and explaining missing/matching competencies.
    """
    return await rag_service.job_match(db, resume_text=payload.resume_text, job_id=payload.job_id)


@router.post(
    "/embed-jobs",
    response_model=RagEmbedJobsResponse,
    status_code=status.HTTP_200_OK,
    summary="Embed database job listings into Qdrant",
)
async def embed_jobs(
    db: DBSession,
    current_user: CurrentUser,
) -> RagEmbedJobsResponse:
    """
    Fetch all active, un-indexed job records in SQL database, compute vector embeddings,
    and index them into Qdrant.
    """
    return await rag_service.embed_jobs(db)
