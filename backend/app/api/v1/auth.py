"""
Auth routes: register, login, refresh token, logout, me, and change-password.
Delegates business logic to the auth_service.
"""

from fastapi import APIRouter, status

from app.api.deps import BearerToken, CurrentUser, DBSession
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserOut, UserUpdate
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user account",
)
async def register(payload: RegisterRequest, db: DBSession):
    """
    Create a new user account with email, password, and display name.
    Performs email duplication checks and password strength validations.
    """
    return await auth_service.register(db, schema=payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user credentials",
)
async def login(payload: LoginRequest, db: DBSession) -> TokenResponse:
    """
    Validate credentials and return access + refresh tokens.
    """
    return await auth_service.login(db, email=payload.email, password=payload.password)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
async def refresh_token(payload: RefreshRequest, db: DBSession) -> TokenResponse:
    """
    Issue a new JWT access + refresh token pair using a valid refresh token.
    """
    return await auth_service.refresh(db, refresh_token=payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout current user",
)
async def logout(
    current_user: CurrentUser,
    credentials: BearerToken,
    db: DBSession,
) -> None:
    """
    Blacklist the caller's JWT access token so it cannot be used again.
    """
    if credentials:
        await auth_service.logout(db, access_token=credentials.credentials)


@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Retrieve current user profile",
)
async def get_me(current_user: CurrentUser) -> UserOut:
    """
    Fetch profile information of the currently authenticated user.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile details",
)
async def update_me(
    payload: UserUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> UserOut:
    """
    Update the authenticated user's profile details.
    """
    from app.crud.crud_user import crud_user
    return await crud_user.update_profile(db, user=current_user, update_data=payload)



@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change user password",
)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> MessageResponse:
    """
    Update password for the current user after validating their old password.
    """
    await auth_service.change_password(
        db,
        user=current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return MessageResponse(message="Password updated successfully.")
