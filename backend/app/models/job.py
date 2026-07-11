"""
Job ORM model.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import ARRAY, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    job_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # full-time | part-time | remote | contract
    experience_level: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # junior | mid | senior
    salary_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    benefits: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Comma-separated skills stored as PostgreSQL array
    skills_required: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True
    )

    apply_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # Whether this job has been embedded and stored in Qdrant
    is_indexed: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    applications: Mapped[list["Application"]] = relationship(  # noqa: F821
        "Application", back_populates="job", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title} company={self.company}>"
