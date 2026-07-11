"""
Database initialisation — run once on app startup.
Creates all tables (if they don't exist) and optionally seeds initial data.
"""


import app.models.application  # noqa: F401
import app.models.job  # noqa: F401
import app.models.resume  # noqa: F401
import app.models.token_blacklist  # noqa: F401

# Import all models here so Base.metadata knows about every table.
# This list must be kept in sync as new models are added.
import app.models.user  # noqa: F401
from app.core.logging import get_logger
from app.db.base import Base
from app.db.session import engine

logger = get_logger(__name__)


async def init_db() -> None:
    """
    Create all database tables on first run.

    In production use Alembic migrations instead of create_all.
    This function is safe to call on every startup — SQLAlchemy only
    creates tables that don't already exist.
    """
    logger.info("Initialising database tables...")
    # Table creation is now handled by Alembic migrations
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready.")
