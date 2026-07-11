"""
Application configuration loaded from environment variables.
Uses Pydantic BaseSettings for automatic validation and type coercion.
"""

import os
from functools import lru_cache

# Prevent system-wide PG env overrides from causing asyncpg configuration crashes
if "PGSSLMODE" in os.environ:
    os.environ.pop("PGSSLMODE")


from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings class. All values come from environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "AI Job Recommendation Assistant"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production

    # ── API ──────────────────────────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "job_assistant"

    # Async DSN (asyncpg driver)
    DATABASE_URL: str = ""

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        else:
            url = self.DATABASE_URL.strip()
            
            # Ensure it uses postgresql+asyncpg:// scheme
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
                
            # Strip invalid asyncpg parameters like supa and sslmode
            if "?" in url:
                base_part, query_part = url.split("?", 1)
                params = query_part.split("&")
                clean_params = []
                for param in params:
                    if "=" in param:
                        key, val = param.split("=", 1)
                        if key.lower() in ("supa", "sslmode", "ssl"):
                            continue
                        clean_params.append(param)
                    else:
                        clean_params.append(param)
                
                # Force asyncpg-compatible SSL parameter
                clean_params.append("ssl=require")
                url = f"{base_part}?{'&'.join(clean_params)}"
            else:
                url = f"{url}?ssl=require"
                
            self.DATABASE_URL = url
        return self

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Password Hashing ─────────────────────────────────────────────────────
    BCRYPT_ROUNDS: int = 12

    # ── AWS S3 ───────────────────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET_NAME: str = "job-assistant-bucket"
    AWS_S3_PRESIGNED_URL_EXPIRY: int = 3600  # seconds

    # ── Qdrant ───────────────────────────────────────────────────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION_JOBS: str = "jobs"
    QDRANT_COLLECTION_RESUMES: str = "resumes"
    QDRANT_VECTOR_SIZE: int = 384  # FastEmbed BAAI/bge-small-en-v1.5

    # ── Groq LLM ─────────────────────────────────────────────────────────────
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_MAX_TOKENS: int = 1024
    GROQ_TEMPERATURE: float = 0.3

    # ── FastEmbed ────────────────────────────────────────────────────────────
    FASTEMBED_MODEL: str = "BAAI/bge-small-en-v1.5"

    # ── Logging ──────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """
    Returns a cached singleton instance of Settings.
    Use as a FastAPI dependency: settings = Depends(get_settings)
    """
    return Settings()


# Module-level convenience export
settings: Settings = get_settings()
