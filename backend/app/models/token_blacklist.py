"""
Token blacklist ORM model.
Stores invalidated JWT JTI values to prevent reuse after logout.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TokenBlacklist(Base):
    __tablename__ = "token_blacklists"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # The JWT's unique identifier claim
    jti: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    # The user this token belonged to (for bulk invalidation on account changes)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # When the token naturally expires — used for scheduled cleanup
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    blacklisted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Composite index to speed up cleanup queries
    __table_args__ = (
        Index("ix_token_blacklist_expires_at", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<TokenBlacklist jti={self.jti} user={self.user_id}>"
