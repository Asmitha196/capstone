import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/student_db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Supabase requires SSL but the asyncpg driver doesn't support the "?sslmode" URL text.
from uuid import uuid4

# We split the URL to remove the query parameters, and pass ssl="require" instead.
if "supabase.com" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0] + "?prepared_statement_cache_size=0"
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={
            "ssl": "require",
            "statement_cache_size": 0,
            "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4().hex}__"
        }
    )
else:
    if "?" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL + "&prepared_statement_cache_size=0"
    else:
        DATABASE_URL = DATABASE_URL + "?prepared_statement_cache_size=0"
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        connect_args={
            "statement_cache_size": 0,
            "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4().hex}__"
        }
    )
SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
Base = declarative_base()

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise
        finally:
            await db.close()
# generator - uses yield and after it uses it can be used in try block 
# after the use it is closed
# prevents the memory leek , connection to db is closed properly
# it creates session for each request and closes it after the request
# ensures that each request has its own session

# For backwards compatibility with other modules in the application
AsyncSessionLocal = SessionLocal
