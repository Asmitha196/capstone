"""
Custom HTTP exception classes for consistent error responses.
All exceptions carry a machine-readable 'code' field alongside the HTTP status.
"""

from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    """Raised when JWT validation fails (missing, expired, or tampered token)."""

    def __init__(self, detail: str = "Could not validate credentials."):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredException(HTTPException):
    """Raised specifically when a JWT has expired."""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ForbiddenException(HTTPException):
    """Raised when the authenticated user lacks permission for an action."""

    def __init__(self, detail: str = "You do not have permission to perform this action."):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(HTTPException):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str = "Resource"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} not found.",
        )


class ConflictException(HTTPException):
    """Raised on duplicate resource creation (e.g. duplicate email)."""

    def __init__(self, detail: str = "Resource already exists."):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class UnprocessableEntityException(HTTPException):
    """Raised when business logic validation fails beyond Pydantic schema checks."""

    def __init__(self, detail: str = "Request could not be processed."):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class ServiceUnavailableException(HTTPException):
    """Raised when an external service (Qdrant, Groq, S3) is unreachable."""

    def __init__(self, service: str = "External service"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"{service} is currently unavailable. Please try again later.",
        )
