"""
Resume ORM model — stores S3 reference and parsed text/skills.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import ARRAY, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,   # one resume per user
        nullable=False,
        index=True,
    )

    # S3 object key — use s3_client.get_presigned_url(s3_key) to download
    s3_key: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(nullable=True)

    # LLM-parsed content
    parsed_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_skills: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    parsed_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Whether this resume's embedding has been stored in Qdrant
    is_indexed: Mapped[bool] = mapped_column(default=False, nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(
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
    user: Mapped["User"] = relationship("User", back_populates="resume")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Resume id={self.id} user_id={self.user_id}>"
