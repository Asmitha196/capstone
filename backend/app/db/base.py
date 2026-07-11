"""
SQLAlchemy declarative base and shared metadata.
Import Base into every model file and point Alembic here.
"""

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    Common base for all ORM models.

    Auto-generates __tablename__ from the class name (snake_case plural).
    Every model that inherits from Base is automatically registered
    in Base.metadata, which Alembic reads for migrations.
    """

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """Derive table name automatically: UserProfile → user_profiles."""
        import re

        name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        # Pluralise naively (handles most cases; override per-model if needed)
        return name + "s" if not name.endswith("s") else name
