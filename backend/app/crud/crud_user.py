"""
User-specific CRUD operations.
Extends CRUDBase with auth-specific queries:
  - get_by_email
  - create_with_password  (accepts raw password, hashes internally)
  - update_password
  - soft_delete (deactivate instead of hard delete)
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """
    User CRUD — all methods are async and accept an AsyncSession.
    The service layer is responsible for transaction management.
    """

    # ── Lookup helpers ────────────────────────────────────────────────────────

    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        """
        Fetch a user by their unique email address.
        Returns None if no matching user exists.
        """
        result = await db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, *, user_id: UUID | str) -> User | None:
        """Fetch a user by their UUID primary key."""
        return await self.get(db, user_id)

    async def exists_by_email(self, db: AsyncSession, *, email: str) -> bool:
        """Return True if an account with this email already exists."""
        user = await self.get_by_email(db, email=email)
        return user is not None

    # ── Create ────────────────────────────────────────────────────────────────

    async def create_with_password(
        self,
        db: AsyncSession,
        *,
        email: str,
        password: str,
        full_name: str,
        role: str = "user",
    ) -> User:
        """
        Create a new user, hashing the raw password before persisting.

        Args:
            db: Async database session.
            email: The user's unique email (normalised to lowercase).
            password: Plain-text password — hashed before storage.
            full_name: Display name.
            role: Role string, defaults to 'user'.

        Returns:
            The newly created User ORM object with a populated UUID.
        """
        user = User(
            email=email.lower().strip(),
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True,
            is_verified=False,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    # ── Update helpers ────────────────────────────────────────────────────────

    async def update_password(
        self,
        db: AsyncSession,
        *,
        user: User,
        new_password: str,
    ) -> User:
        """
        Hash and persist a new password for the given user.

        Args:
            db: Async database session.
            user: The ORM user object to update.
            new_password: The new plain-text password.

        Returns:
            Updated User object.
        """
        user.hashed_password = hash_password(new_password)
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    async def update_profile(
        self,
        db: AsyncSession,
        *,
        user: User,
        update_data: UserUpdate,
    ) -> User:
        """
        Partially update user profile fields.
        Only fields set in update_data are written.
        """
        return await self.update(db, db_obj=user, obj_in=update_data)

    # ── Activation ────────────────────────────────────────────────────────────

    async def deactivate(self, db: AsyncSession, *, user: User) -> User:
        """Soft-delete: mark user as inactive instead of hard deleting."""
        user.is_active = False
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    async def verify_email(self, db: AsyncSession, *, user: User) -> User:
        """Mark the user's email as verified."""
        user.is_verified = True
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user


# Module-level singleton — import and use directly in services
crud_user = CRUDUser(User)
