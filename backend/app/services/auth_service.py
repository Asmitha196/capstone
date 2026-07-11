"""
Authentication service layer.
Orchestrates registration, login, token refresh, logout/revocation, and password changes.
"""

from datetime import UTC, datetime

from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, CredentialsException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.crud.crud_token_blacklist import crud_token_blacklist
from app.crud.crud_user import crud_user
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse


class AuthService:
    """
    Orchestrates business logic for user authentication.
    Communicates with the database via CRUD helper singletons.
    """

    async def register(self, db: AsyncSession, *, schema: RegisterRequest) -> User:
        """
        Register a new user account.

        Args:
            db: Async database session.
            schema: The validated registration details.

        Returns:
            The created User model.

        Raises:
            ConflictException: If the email is already in use.
        """
        # Normalise email
        email = schema.email.lower().strip()

        # Check uniqueness
        if await crud_user.exists_by_email(db, email=email):
            raise ConflictException("An account with this email already exists.")

        # Create user
        return await crud_user.create_with_password(
            db,
            email=email,
            password=schema.password,
            full_name=schema.full_name,
        )

    async def login(
        self, db: AsyncSession, *, email: str, password: str
    ) -> TokenResponse:
        """
        Authenticate a user's credentials and issue access + refresh tokens.

        Args:
            db: Async database session.
            email: Account email.
            password: Plain password.

        Returns:
            TokenResponse containing access, refresh token and type.

        Raises:
            CredentialsException: On incorrect credentials or inactive account.
        """
        email = email.lower().strip()
        user = await crud_user.get_by_email(db, email=email)

        if not user or not verify_password(password, user.hashed_password):
            raise CredentialsException("Incorrect email or password.")

        if not user.is_active:
            raise CredentialsException("User account is inactive.")

        # Generate tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh(self, db: AsyncSession, *, refresh_token: str) -> TokenResponse:
        """
        Issue a new access token using a valid, non-expired refresh token.

        Args:
            db: Async database session.
            refresh_token: The refresh JWT.

        Returns:
            TokenResponse containing new access + refresh tokens.

        Raises:
            CredentialsException: If token is invalid/expired or user is inactive.
        """
        try:
            payload = decode_token(refresh_token)
        except JWTError as exc:
            if "expired" in str(exc).lower():
                raise CredentialsException("Refresh token has expired. Please log in again.") from exc
            raise CredentialsException("Invalid refresh token.") from exc

        if payload.get("type") != "refresh":
            raise CredentialsException("Invalid token type. Expected a refresh token.")

        user_id = payload.get("sub")
        if not user_id:
            raise CredentialsException("Refresh token is missing user subject.")

        user = await crud_user.get_by_id(db, user_id=user_id)
        if not user or not user.is_active:
            raise CredentialsException("User not found or inactive.")

        # Rotate tokens for security (issue a fresh pair)
        new_access = create_access_token(str(user.id))
        new_refresh = create_refresh_token(str(user.id))

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            token_type="bearer",
        )

    async def logout(self, db: AsyncSession, *, access_token: str) -> None:
        """
        Log a user out by blacklisting their access token.

        Args:
            db: Async database session.
            access_token: The raw access token from Bearer auth.
        """
        try:
            payload = decode_token(access_token)
        except JWTError:
            # Token is already invalid, no need to blacklist
            return

        jti = payload.get("jti")
        # In this implementation, if jti is not in payload, we generate one or extract it.
        # Let's ensure if it has a jti or fallback.
        if not jti:
            # Fallback: if no JTI claim exists, we can use the signature or hash,
            # or just skip if the token isn't fully set up for JTI.
            # But let's check if our token has it. By default, jose.jwt encodes whatever we send.
            # In security.py, we did not explicitly put a JTI. Let's add it there or extract sub + exp.
            # Let's use `jti = payload.get("sub") + "_" + str(payload.get("exp"))` if JTI isn't present.
            jti = f"{payload.get('sub')}_{payload.get('exp')}"

        user_id = payload.get("sub", "")
        exp = payload.get("exp")

        expires_at = datetime.fromtimestamp(exp, tz=UTC) if exp else datetime.now(UTC)

        await crud_token_blacklist.add(
            db,
            jti=jti,
            user_id=user_id,
            expires_at=expires_at,
        )

    async def change_password(
        self,
        db: AsyncSession,
        *,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        """
        Change a user's password after verifying their current password.

        Args:
            db: Async database session.
            user: The user changing their password.
            current_password: Plain text current password.
            new_password: Plain text new password.

        Raises:
            CredentialsException: If current password verification fails.
        """
        if not verify_password(current_password, user.hashed_password):
            raise CredentialsException("Incorrect current password.")

        await crud_user.update_password(db, user=user, new_password=new_password)


# Service singleton
auth_service = AuthService()
