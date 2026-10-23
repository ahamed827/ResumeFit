from app.api.deps import get_current_user
from app.core.rate_limiter import rate_limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(req: UserRegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    # Rate limit: 5 registrations per hour per IP
    await rate_limiter.check_rate_limit(
        f"rate:register:{client_ip}", max_requests=5, window_seconds=3600
    )

    service = AuthService(db)
    return await service.register(req, ip_address=client_ip)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(req: UserLoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    # Rate limit: 5 attempts per 15 minutes per IP/email
    rate_key = f"rate:login:{client_ip}:{req.email.lower()}"
    await rate_limiter.check_rate_limit(rate_key, max_requests=5, window_seconds=900)

    service = AuthService(db)
    return await service.login(req, ip_address=client_ip)


@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_tokens(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh_tokens(req.refresh_token)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.logout(req.refresh_token)
    return {"message": "Successfully logged out."}


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.forgot_password(req.email)
    return {
        "message": "If an account matches that email address, a password reset link has been dispatched."
    }


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.reset_password(req.token, req.new_password)
    return {"message": "Password has been successfully updated. You may now log in."}


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
