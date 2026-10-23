import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.config import settings
from app.core.errors import AuthenticationError, BadRequestError, ConflictError, NotFoundError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.integrations.email_service import email_service
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit_repo = AuditRepository(db)

    async def register(
        self, req: UserRegisterRequest, ip_address: Optional[str] = None
    ) -> UserResponse:
        existing = await self.user_repo.get_by_email(req.email)
        if existing:
            raise ConflictError("An account with this email address already exists.")

        password_hash = get_password_hash(req.password)
        user = await self.user_repo.create(
            email=req.email, password_hash=password_hash, full_name=req.full_name, role=req.role
        )

        await self.audit_repo.log_action(
            action="USER_REGISTER",
            entity_type="USER",
            user_id=user.id,
            entity_id=str(user.id),
            meta_info={"email": user.email, "role": user.role.value},
            ip_address=ip_address,
        )

        return UserResponse.model_validate(user)

    async def login(self, req: UserLoginRequest, ip_address: Optional[str] = None) -> TokenResponse:
        user = await self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError(
                "This user account has been disabled. Please contact support."
            )

        access_token = create_access_token(subject=str(user.id), role=user.role.value)
        refresh_token = create_refresh_token(subject=str(user.id))

        # Store refresh token hash for rotation & revocation tracking
        token_hash = hash_token(refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.user_repo.create_refresh_token(
            user_id=user.id, token_hash=token_hash, expires_at=expires_at
        )

        await self.audit_repo.log_action(
            action="USER_LOGIN",
            entity_type="USER",
            user_id=user.id,
            entity_id=str(user.id),
            ip_address=ip_address,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def refresh_tokens(self, refresh_token_str: str) -> TokenResponse:
        """Implements refresh-token rotation."""
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type. Refresh token required.")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Invalid token payload.")

        user_id = uuid.UUID(user_id_str)
        token_hash = hash_token(refresh_token_str)
        token_record = await self.user_repo.get_valid_refresh_token(token_hash)
        if not token_record:
            raise AuthenticationError("Refresh token has expired, been revoked, or is invalid.")

        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User is no longer active.")

        # Revoke the used refresh token (Rotation)
        await self.user_repo.revoke_refresh_token(token_hash)

        # Issue new token pair
        new_access = create_access_token(subject=str(user.id), role=user.role.value)
        new_refresh = create_refresh_token(subject=str(user.id))
        new_hash = hash_token(new_refresh)
        new_expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        await self.user_repo.create_refresh_token(
            user_id=user.id, token_hash=new_hash, expires_at=new_expires_at
        )

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def logout(self, refresh_token_str: str) -> bool:
        try:
            token_hash = hash_token(refresh_token_str)
            await self.user_repo.revoke_refresh_token(token_hash)
            return True
        except Exception:
            return False

    async def forgot_password(self, email: str) -> bool:
        user = await self.user_repo.get_by_email(email)
        if not user:
            # Prevent email enumeration attacks; return True without revealing nonexistence
            return True

        # Generate single-use reset token
        reset_token = create_access_token(
            subject=str(user.id),
            role=user.role.value,
            expires_delta=timedelta(hours=1),
            extra_claims={"type": "password_reset"},
        )
        return await email_service.send_password_reset_email(user.email, reset_token)

    async def reset_password(self, token_str: str, new_password: str) -> bool:
        payload = decode_token(token_str)
        if payload.get("type") != "password_reset":
            raise BadRequestError("Invalid password reset token.")

        user_id_str = payload.get("sub")
        user = await self.user_repo.get_by_id(uuid.UUID(user_id_str))
        if not user:
            raise NotFoundError("User", user_id_str)

        new_hash = get_password_hash(new_password)
        await self.user_repo.update(user, password_hash=new_hash)
        return True
