import uuid
from typing import List, Optional, Tuple

from app.models.job import AnalysisStatus, Job, JobSourceType
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class JobRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, job_id: uuid.UUID) -> Optional[Job]:
        stmt = select(Job).where(Job.id == job_id, Job.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_id_and_user(self, job_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Job]:
        stmt = select(Job).where(Job.id == job_id, Job.user_id == user_id, Job.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20, search: Optional[str] = None
    ) -> Tuple[List[Job], int]:
        base_filter = [Job.user_id == user_id, Job.deleted_at.is_(None)]
        if search:
            search_term = f"%{search}%"
            base_filter.append(Job.title.ilike(search_term) | Job.company_name.ilike(search_term))

        total_stmt = select(func.count(Job.id)).where(*base_filter)
        total_res = await self.db.execute(total_stmt)
        total = total_res.scalar_one()

        stmt = (
            select(Job)
            .where(*base_filter)
            .order_by(Job.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create(
        self,
        user_id: uuid.UUID,
        title: str,
        raw_description: str,
        company_name: Optional[str] = None,
        source_type: JobSourceType = JobSourceType.PASTED,
        file_url: Optional[str] = None,
        analysis_status: AnalysisStatus = AnalysisStatus.PENDING,
    ) -> Job:
        job = Job(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            company_name=company_name,
            source_type=source_type,
            raw_description=raw_description,
            file_url=file_url,
            analysis_status=analysis_status,
        )
        self.db.add(job)
        await self.db.flush()
        return job

    async def update(self, job: Job, **kwargs) -> Job:
        for key, value in kwargs.items():
            if hasattr(job, key):
                setattr(job, key, value)
        await self.db.flush()
        return job

    async def soft_delete(self, job: Job) -> None:
        job.soft_delete()
        await self.db.flush()

    async def count_all_completed(self) -> int:
        stmt = select(func.count(Job.id)).where(
            Job.analysis_status == AnalysisStatus.COMPLETED, Job.deleted_at.is_(None)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()
