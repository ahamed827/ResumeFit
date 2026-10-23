import uuid
from typing import List, Optional, Tuple

from app.models.match import Match, MatchStatus
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class MatchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, match_id: uuid.UUID) -> Optional[Match]:
        stmt = select(Match).where(Match.id == match_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_id_and_user(self, match_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Match]:
        stmt = select(Match).where(Match.id == match_id, Match.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_resume_and_job(
        self, resume_id: uuid.UUID, job_id: uuid.UUID
    ) -> Optional[Match]:
        stmt = select(Match).where(Match.resume_id == resume_id, Match.job_id == job_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Match], int]:
        total_stmt = select(func.count(Match.id)).where(Match.user_id == user_id)
        total_res = await self.db.execute(total_stmt)
        total = total_res.scalar_one()

        stmt = (
            select(Match)
            .where(Match.user_id == user_id)
            .order_by(Match.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create(
        self,
        user_id: uuid.UUID,
        resume_id: uuid.UUID,
        job_id: uuid.UUID,
        status: MatchStatus = MatchStatus.PENDING,
    ) -> Match:
        match_obj = Match(
            id=uuid.uuid4(), user_id=user_id, resume_id=resume_id, job_id=job_id, status=status
        )
        self.db.add(match_obj)
        await self.db.flush()
        return match_obj

    async def update(self, match_obj: Match, **kwargs) -> Match:
        for key, value in kwargs.items():
            if hasattr(match_obj, key):
                setattr(match_obj, key, value)
        await self.db.flush()
        return match_obj

    async def delete(self, match_obj: Match) -> None:
        await self.db.delete(match_obj)
        await self.db.flush()

    async def count_all(self) -> int:
        stmt = select(func.count(Match.id))
        res = await self.db.execute(stmt)
        return res.scalar_one()
