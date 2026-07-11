"""
Job service layer.
Coordinates CRUD operations for jobs.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.crud.crud_job import crud_job
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


class JobService:
    """
    Orchestrates business logic for Job listings and management.
    Communicates with database via crud_job and supports future Qdrant indexing integration.
    """

    async def list_jobs(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        location: str | None = None,
        job_type: str | None = None,
        experience_level: str | None = None,
        search: str | None = None,
        is_active: bool | None = True,
    ) -> tuple[int, list[Job]]:
        """List and search jobs with filters."""
        return await crud_job.get_multi_filtered(
            db,
            skip=skip,
            limit=limit,
            location=location,
            job_type=job_type,
            experience_level=experience_level,
            search=search,
            is_active=is_active,
        )

    async def create_job(self, db: AsyncSession, *, schema: JobCreate) -> Job:
        """Create a new job listing."""
        job = await crud_job.create(db, obj_in=schema)
        # TODO: Trigger background task to embed and index the job in Qdrant
        return job

    async def get_job(self, db: AsyncSession, *, job_id: UUID | str) -> Job:
        """Retrieve a single job listing by ID."""
        job = await crud_job.get(db, job_id)
        if not job:
            raise NotFoundException("Job")
        return job

    async def update_job(
        self, db: AsyncSession, *, job_id: UUID | str, schema: JobUpdate
    ) -> Job:
        """Update an existing job listing."""
        job = await self.get_job(db, job_id=job_id)
        return await crud_job.update(db, db_obj=job, obj_in=schema)

    async def delete_job(self, db: AsyncSession, *, job_id: UUID | str) -> Job:
        """Delete a job listing."""
        await self.get_job(db, job_id=job_id)
        deleted_job = await crud_job.delete(db, id=job_id)
        if not deleted_job:
            raise NotFoundException("Job")
        return deleted_job


# Service singleton
job_service = JobService()
