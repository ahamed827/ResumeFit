import uuid
from typing import List, Optional

from app.core.errors import AuthenticationError, PermissionDeniedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    token_auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token_auth or not token_auth.credentials:
        raise AuthenticationError("Authorization header is missing or malformed.")

    payload = decode_token(token_auth.credentials)
    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type. Access token required.")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Token payload missing subject identifier.")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid user ID format in token.")

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise AuthenticationError("User not found.")

    if not user.is_active:
        raise PermissionDeniedError("Account is disabled. Please contact administrator.")

    return user


def require_role(roles: List[UserRole]):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise PermissionDeniedError(
                f"Action restricted to roles: {', '.join([r.value for r in roles])}."
            )
        return current_user

    return role_checker


require_admin = require_role([UserRole.ADMIN])
require_candidate_or_admin = require_role([UserRole.CANDIDATE, UserRole.ADMIN])
