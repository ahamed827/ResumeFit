import uuid
from typing import List, Optional, Tuple

from app.models.summary import ResumeSummary
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class SummaryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, summary_id: uuid.UUID) -> Optional[ResumeSummary]:
        stmt = select(ResumeSummary).where(ResumeSummary.id == summary_id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_id_and_user(
        self, summary_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[ResumeSummary]:
        stmt = select(ResumeSummary).where(
            ResumeSummary.id == summary_id, ResumeSummary.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> Tuple[List[ResumeSummary], int]:
        total_stmt = select(func.count(ResumeSummary.id)).where(ResumeSummary.user_id == user_id)
        total_res = await self.db.execute(total_stmt)
        total = total_res.scalar_one()

        stmt = (
            select(ResumeSummary)
            .where(ResumeSummary.user_id == user_id)
            .order_by(ResumeSummary.created_at.desc())
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
        generated_summary: str,
        model_name: Optional[str] = None,
        prompt_version: Optional[str] = None,
    ) -> ResumeSummary:
        summary = ResumeSummary(
            id=uuid.uuid4(),
            user_id=user_id,
            resume_id=resume_id,
            job_id=job_id,
            generated_summary=generated_summary,
            model_name=model_name,
            prompt_version=prompt_version,
        )
        self.db.add(summary)
        await self.db.flush()
        return summary
