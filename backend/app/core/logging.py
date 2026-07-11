"""
Structured JSON logging configuration.
Sets up a single logger for the entire application with consistent formatting.
"""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure the root logger for the application.
    Outputs structured, leveled log messages to stdout.
    Call this once at application startup in main.py lifespan.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Apply to root logger — propagates to all child loggers
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Reduce noise from noisy third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DEBUG else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """
    Returns a named logger.

    Usage:
        logger = get_logger(__name__)
        logger.info("Something happened")
    """
    return logging.getLogger(name)
