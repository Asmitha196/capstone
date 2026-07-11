"""
Job API endpoints.
Provides list, search, retrieve, create, update, and delete actions for job listings.
"""

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DBSession
from app.schemas.job import JobCreate, JobListOut, JobOut, JobUpdate
from app.services.job_service import job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get(
    "",
    response_model=JobListOut,
    status_code=status.HTTP_200_OK,
    summary="List and filter job listings",
)
async def list_jobs(
    db: DBSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    location: str | None = Query(default=None),
    job_type: str | None = Query(default=None, description="e.g. full-time, part-time, remote, contract"),
    experience_level: str | None = Query(default=None, description="e.g. junior, mid, senior"),
    search: str | None = Query(default=None, description="Text search on title, company, or description"),
) -> JobListOut:
    """
    Retrieve job listings with optional filtering on location, job type,
    experience level, and free-text search.
    """
    total, items = await job_service.list_jobs(
        db,
        skip=skip,
        limit=limit,
        location=location,
        job_type=job_type,
        experience_level=experience_level,
        search=search,
    )
    return JobListOut(total=total, items=items, skip=skip, limit=limit)


@router.post(
    "",
    response_model=JobOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job listing",
)
async def create_job(
    payload: JobCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> JobOut:
    """
    Create a new job listing.
    Requires caller to be authenticated.
    """
    return await job_service.create_job(db, schema=payload)


@router.get(
    "/{id}",
    response_model=JobOut,
    status_code=status.HTTP_200_OK,
    summary="Retrieve single job details",
)
async def get_job(
    id: UUID,
    db: DBSession,
) -> JobOut:
    """
    Retrieve a single job listing by UUID identifier.
    """
    return await job_service.get_job(db, job_id=id)


@router.put(
    "/{id}",
    response_model=JobOut,
    status_code=status.HTTP_200_OK,
    summary="Update an existing job listing",
)
async def update_job(
    id: UUID,
    payload: JobUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> JobOut:
    """
    Update details of a job listing by UUID.
    Requires caller to be authenticated.
    """
    return await job_service.update_job(db, job_id=id, schema=payload)


@router.delete(
    "/{id}",
    response_model=JobOut,
    status_code=status.HTTP_200_OK,
    summary="Delete a job listing",
)
async def delete_job(
    id: UUID,
    db: DBSession,
    current_user: CurrentUser,
) -> JobOut:
    """
    Remove a job listing by UUID.
    Requires caller to be authenticated.
    """
    return await job_service.delete_job(db, job_id=id)
