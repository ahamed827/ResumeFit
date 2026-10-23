import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from app.db.base import utc_now
from app.models.user import RefreshToken, User, UserRole
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email.lower().strip(), User.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create(self, email: str, password_hash: str, full_name: str, role: UserRole) -> User:
        user = User(
            id=uuid.uuid4(),
            email=email.lower().strip(),
            password_hash=password_hash,
            full_name=full_name.strip(),
            role=role,
            is_active=True,
            email_verified=False,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self.db.flush()
        return user

    async def soft_delete(self, user: User) -> None:
        user.soft_delete()
        await self.db.flush()

    async def list_users(self, skip: int = 0, limit: int = 50) -> Tuple[List[User], int]:
        total_stmt = select(func.count(User.id)).where(User.deleted_at.is_(None))
        total_res = await self.db.execute(total_stmt)
        total = total_res.scalar_one()

        stmt = (
            select(User)
            .where(User.deleted_at.is_(None))
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def count_users(self) -> int:
        stmt = select(func.count(User.id)).where(User.deleted_at.is_(None))
        res = await self.db.execute(stmt)
        return res.scalar_one()

    # Refresh tokens
    async def create_refresh_token(
        self, user_id: uuid.UUID, token_hash: str, expires_at: datetime
    ) -> RefreshToken:
        token_record = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=utc_now(),
        )
        self.db.add(token_record)
        await self.db.flush()
        return token_record

    async def get_valid_refresh_token(self, token_hash: str) -> Optional[RefreshToken]:
        now = utc_now()
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def revoke_refresh_token(self, token_hash: str) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(revoked_at=utc_now())
        )
        await self.db.execute(stmt)
        await self.db.flush()
