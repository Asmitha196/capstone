"""
Unit tests for AuthService.
Tests business logic, validations, and token operations in isolation.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, CredentialsException
from app.core.security import verify_password
from app.schemas.auth import RegisterRequest
from app.services.auth_service import auth_service


@pytest.mark.asyncio
async def test_register_user_success(db: AsyncSession) -> None:
    """Test successful user registration."""
    schema = RegisterRequest(
        email="test_user@example.com",
        password="SecurePassword123",
        full_name="Test User",
    )
    user = await auth_service.register(db, schema=schema)
    
    assert user.id is not None
    assert user.email == "test_user@example.com"
    assert user.full_name == "Test User"
    assert verify_password("SecurePassword123", user.hashed_password)
    assert user.is_active is True
    assert user.is_verified is False


@pytest.mark.asyncio
async def test_register_user_duplicate_email(db: AsyncSession) -> None:
    """Test registering a user with an already existing email."""
    schema1 = RegisterRequest(
        email="duplicate@example.com",
        password="SecurePassword123",
        full_name="First User",
    )
    await auth_service.register(db, schema=schema1)
    
    schema2 = RegisterRequest(
        email="Duplicate@example.com",  # case-insensitive check
        password="AnotherSecurePassword123",
        full_name="Second User",
    )
    with pytest.raises(ConflictException) as exc_info:
        await auth_service.register(db, schema=schema2)
    assert "email already exists" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_login_success(db: AsyncSession) -> None:
    """Test successful user login validation and token response."""
    # Seed user
    schema = RegisterRequest(
        email="login@example.com",
        password="SecurePassword123",
        full_name="Login User",
    )
    await auth_service.register(db, schema=schema)

    # Login
    response = await auth_service.login(
        db, email="login@example.com", password="SecurePassword123"
    )
    
    assert response.access_token is not None
    assert response.refresh_token is not None
    assert response.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password(db: AsyncSession) -> None:
    """Test login fails with incorrect password."""
    schema = RegisterRequest(
        email="wrong_password@example.com",
        password="SecurePassword123",
        full_name="Login User",
    )
    await auth_service.register(db, schema=schema)

    with pytest.raises(CredentialsException) as exc_info:
        await auth_service.login(
            db, email="wrong_password@example.com", password="WrongPassword"
        )
    assert "Incorrect email or password" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_login_inactive_user(db: AsyncSession) -> None:
    """Test login fails if the user account is deactivated."""
    schema = RegisterRequest(
        email="inactive@example.com",
        password="SecurePassword123",
        full_name="Inactive User",
    )
    user = await auth_service.register(db, schema=schema)
    
    # Deactivate user
    user.is_active = False
    db.add(user)
    await db.flush()

    with pytest.raises(CredentialsException) as exc_info:
        await auth_service.login(
            db, email="inactive@example.com", password="SecurePassword123"
        )
    assert "inactive" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_change_password_success(db: AsyncSession) -> None:
    """Test successful password modification."""
    schema = RegisterRequest(
        email="change_pwd@example.com",
        password="SecurePassword123",
        full_name="Change Password User",
    )
    user = await auth_service.register(db, schema=schema)

    # Change password
    await auth_service.change_password(
        db,
        user=user,
        current_password="SecurePassword123",
        new_password="NewSecurePassword987",
    )

    # Verify logging in with new password works
    response = await auth_service.login(
        db, email="change_pwd@example.com", password="NewSecurePassword987"
    )
    assert response.access_token is not None
