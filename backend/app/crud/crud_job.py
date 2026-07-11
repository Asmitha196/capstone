"""
Job-specific CRUD operations.
"""


from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


class CRUDJob(CRUDBase[Job, JobCreate, JobUpdate]):
    """
    CRUD class for Job model.
    Inherits generic get, get_multi, create, update, delete from CRUDBase.
    """

    async def get_multi_filtered(
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
        """
        Fetch jobs filtering by location, type, experience level, and a text search term.
        Returns a tuple of (total_count, jobs_list) for pagination meta headers.
        """
        filters = []
        if is_active is not None:
            filters.append(Job.is_active == is_active)
        if location:
            filters.append(Job.location.icontains(location))
        if job_type:
            filters.append(Job.job_type == job_type)
        if experience_level:
            filters.append(Job.experience_level == experience_level)
        if search:
            # Split search into words and match if any of the fields contain any word
            words = [w.strip("?,.!") for w in search.lower().split() if len(w) > 2]
            if not words:
                words = [search.lower()]
            
            word_filters = []
            for word in words:
                word_filters.append(
                    func.lower(Job.title).contains(word)
                    | func.lower(Job.company).contains(word)
                    | func.lower(Job.description).contains(word)
                )
            filters.append(or_(*word_filters))

        # Base query
        query = select(Job).where(and_(*filters))

        # Total count query
        count_query = select(func.count()).select_from(query.subquery())
        total_count_result = await db.execute(count_query)
        total = total_count_result.scalar_one()

        # Apply skip & limit for the list query
        list_query = query.offset(skip).limit(limit).order_by(Job.created_at.desc())
        list_result = await db.execute(list_query)
        items = list(list_result.scalars().all())

        return total, items


# Module-level singleton
crud_job = CRUDJob(Job)
