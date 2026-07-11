"""
Generic async CRUD base class.
Provides reusable get / get_multi / create / update / delete operations
that every resource-specific CRUD class inherits from.
"""

from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

# Generic type vars
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic async CRUD operations tied to a SQLAlchemy ORM model.

    Usage:
        class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
            ...
        crud_user = CRUDUser(User)
    """

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    # ── Read ─────────────────────────────────────────────────────────────────

    async def get(self, db: AsyncSession, id: UUID | str) -> ModelType | None:
        """Fetch a single record by primary key. Returns None if not found."""
        if isinstance(id, str):
            import uuid
            try:
                id = uuid.UUID(id)
            except ValueError:
                return None
        result = await db.execute(
            select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Fetch a paginated list of records."""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    # ── Create ────────────────────────────────────────────────────────────────

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: CreateSchemaType,
    ) -> ModelType:
        """
        Create a new record from a Pydantic schema.
        Calls db.flush() to get the generated PK before the session commits.
        """
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    # ── Update ────────────────────────────────────────────────────────────────

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """
        Partially update an existing ORM object.
        Accepts either a Pydantic schema or a plain dict.
        Only fields explicitly set in the payload are written.
        """
        update_data = (
            obj_in
            if isinstance(obj_in, dict)
            else obj_in.model_dump(exclude_unset=True)
        )

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    # ── Delete ────────────────────────────────────────────────────────────────

    async def delete(self, db: AsyncSession, *, id: UUID | str) -> ModelType | None:
        """
        Delete a record by primary key.
        Returns the deleted object or None if it didn't exist.
        """
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.flush()
        return obj
