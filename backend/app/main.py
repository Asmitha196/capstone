"""
FastAPI application factory.

This module:
  1. Configures structured logging.
  2. Defines the async lifespan (startup + shutdown hooks).
  3. Creates and configures the FastAPI app instance.
  4. Registers global middleware (CORS, GZip).
  5. Mounts the versioned API router.
  6. Adds a global exception handler for clean JSON error bodies.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging
from app.db.init_db import init_db
from app.db.session import engine

# Configure logging first so every startup message is captured
setup_logging()
logger = get_logger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Async context manager for application startup and shutdown.

    Startup:
      - Initialise PostgreSQL tables (create_all).
      - Log configuration summary.

    Shutdown:
      - Dispose the SQLAlchemy connection pool cleanly.
    """
    # ── Startup ────────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info(f"  {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"  Environment : {settings.ENVIRONMENT}")
    logger.info(f"  Debug mode  : {settings.DEBUG}")
    logger.info("=" * 60)

    logger.info("Connecting to PostgreSQL...")
    await init_db()
    logger.info("PostgreSQL ready.")

    logger.info("Application startup complete. Ready to serve requests.")
    yield  # ── Application runs here ──────────────────────────────────────────

    # ── Shutdown ───────────────────────────────────────────────────────────────
    logger.info("Shutting down — disposing database connection pool...")
    await engine.dispose()
    logger.info("Shutdown complete.")


# ── App factory ───────────────────────────────────────────────────────────────
def create_app() -> FastAPI:
    """
    Construct and return the configured FastAPI application.
    Separated into a factory function to support test overrides.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "AI-Powered Job Recommendation Assistant API. "
            "Provides job search, vector-similarity recommendations, "
            "resume parsing, and an LLM-powered career chat assistant."
        ),
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if settings.DEBUG else None,
        docs_url=f"{settings.API_V1_PREFIX}/docs" if settings.DEBUG else None,
        redoc_url=f"{settings.API_V1_PREFIX}/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # ── Middleware ─────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # ── Global exception handler ──────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(f"Unhandled exception on {request.method} {request.url}: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected internal server error occurred.",
                "path": str(request.url),
            },
        )

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health_check() -> dict:
        """Lightweight liveness probe — returns 200 OK when the app is running."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    return app


# ── Module-level app instance (used by Uvicorn) ───────────────────────────────
app: FastAPI = create_app()
