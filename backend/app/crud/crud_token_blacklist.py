"""
Token blacklist CRUD operations.
Handles storing revoked JWTs and cleaning up expired entries.
"""

from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.token_blacklist import TokenBlacklist


class CRUDTokenBlacklist:
    """
    CRUD for JWT token blacklisting.
    Used during logout to prevent reuse of revoked tokens.
    """

    async def add(
        self,
        db: AsyncSession,
        *,
        jti: str,
        user_id: str,
        expires_at: datetime,
    ) -> TokenBlacklist:
        """
        Add a token JTI to the blacklist.

        Args:
            db: Async database session.
            jti: The JWT's unique identifier claim.
            user_id: The subject (user ID) this token belonged to.
            expires_at: When the token naturally expires — used for cleanup.

        Returns:
            The created TokenBlacklist record.
        """
        entry = TokenBlacklist(
            jti=jti,
            user_id=str(user_id),
            expires_at=expires_at,
            blacklisted_at=datetime.now(UTC),
        )
        db.add(entry)
        await db.flush()
        return entry

    async def is_blacklisted(self, db: AsyncSession, *, jti: str) -> bool:
        """Return True if the given JTI has been blacklisted (i.e. logged out)."""
        result = await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.jti == jti)
        )
        return result.scalar_one_or_none() is not None

    async def purge_expired(self, db: AsyncSession) -> int:
        """
        Delete all blacklist entries whose natural expiry has passed.
        Should be called periodically (e.g. via a scheduled background task).

        Returns:
            Number of rows deleted.
        """
        result = await db.execute(
            delete(TokenBlacklist).where(
                TokenBlacklist.expires_at < datetime.now(UTC)
            )
        )
        await db.flush()
        return result.rowcount  # type: ignore[return-value]

    async def revoke_all_for_user(self, db: AsyncSession, *, user_id: str) -> None:
        """
        Revoke all tokens for a given user.
        Used when a password is changed or the account is deactivated.
        NOTE: This only covers tokens already in the blacklist.
        For true all-device logout, add a 'token_version' counter to the User model.
        """
        await db.execute(
            delete(TokenBlacklist).where(TokenBlacklist.user_id == str(user_id))
        )
        await db.flush()


# Module-level singleton
crud_token_blacklist = CRUDTokenBlacklist()
