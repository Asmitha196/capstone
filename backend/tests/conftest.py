"""
Pytest configuration and global fixtures.
Sets up an in-memory SQLite database using aiosqlite for isolated and fast tests.
Overrides the get_db dependency in the FastAPI application.
"""

import asyncio
import json
import sqlite3
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import ARRAY

from app.db.base import Base
from app.db.session import get_db
from app.main import app

sqlite3.register_adapter(list, json.dumps)

# ── Compile PG ARRAY for SQLite ──────────────────────────────────────────────
@compiles(ARRAY, "sqlite")
def compile_array_sqlite(element: Any, compiler: Any, **kw: Any) -> str:
    """Compile PostgreSQL ARRAY type to TEXT in SQLite for testing compatibility."""
    return "TEXT"


# ── SQLite Database Setup ─────────────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestAsyncSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db() -> AsyncGenerator[None, None]:
    """Create all tables in the in-memory database before running tests."""
    # Import all models to ensure metadata is registered
    import app.models.application  # noqa: F401
    import app.models.job  # noqa: F401
    import app.models.resume  # noqa: F401
    import app.models.token_blacklist  # noqa: F401
    import app.models.user  # noqa: F401

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated database session per test, wrapped in a transaction rollback."""
    async with test_engine.connect() as conn:
        transaction = await conn.begin()
        async with TestAsyncSessionLocal(bind=conn) as session:
            yield session
            await session.close()
        await transaction.rollback()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTPX AsyncClient configured to request the FastAPI application with mocked DB."""
    # Override get_db dependency
    async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
        yield db

    app.dependency_overrides[get_db] = _get_test_db
    
    # Use ASGITransport for testing async endpoint handlers
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
        
    app.dependency_overrides.clear()
