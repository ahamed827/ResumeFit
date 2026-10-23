import uuid
from typing import Dict, List, Optional, Tuple

from app.models.application import Application, ApplicationStatus
from app.models.job import Job
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class ApplicationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, application_id: uuid.UUID) -> Optional[Application]:
        stmt = (
            select(Application)
            .options(selectinload(Application.job))
            .where(Application.id == application_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_id_and_user(
        self, application_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Application]:
        stmt = (
            select(Application)
            .options(selectinload(Application.job))
            .where(Application.id == application_id, Application.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        status: Optional[ApplicationStatus] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[Application], int]:
        query = (
            select(Application)
            .join(Job, Application.job_id == Job.id)
            .options(selectinload(Application.job))
            .where(Application.user_id == user_id)
        )
        count_query = (
            select(func.count(Application.id))
            .join(Job, Application.job_id == Job.id)
            .where(Application.user_id == user_id)
        )

        if status:
            query = query.where(Application.status == status)
            count_query = count_query.where(Application.status == status)

        if search:
            search_term = f"%{search}%"
            query = query.where(Job.title.ilike(search_term) | Job.company_name.ilike(search_term))
            count_query = count_query.where(
                Job.title.ilike(search_term) | Job.company_name.ilike(search_term)
            )

        total_res = await self.db.execute(count_query)
        total = total_res.scalar_one()

        query = query.order_by(Application.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def create(
        self,
        user_id: uuid.UUID,
        job_id: uuid.UUID,
        resume_id: Optional[uuid.UUID] = None,
        status: ApplicationStatus = ApplicationStatus.SAVED,
        applied_at=None,
        deadline=None,
        notes: Optional[str] = None,
    ) -> Application:
        app = Application(
            id=uuid.uuid4(),
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            status=status,
            applied_at=applied_at,
            deadline=deadline,
            notes=notes,
        )
        self.db.add(app)
        await self.db.flush()
        return app

    async def update(self, app: Application, **kwargs) -> Application:
        for key, value in kwargs.items():
            if hasattr(app, key) and value is not None:
                setattr(app, key, value)
        await self.db.flush()
        return app

    async def delete(self, app: Application) -> None:
        await self.db.delete(app)
        await self.db.flush()

    async def get_status_counts(self, user_id: uuid.UUID) -> Dict[str, int]:
        stmt = (
            select(Application.status, func.count(Application.id))
            .where(Application.user_id == user_id)
            .group_by(Application.status)
        )
        res = await self.db.execute(stmt)
        counts = {s.value: 0 for s in ApplicationStatus}
        for status_enum, count in res.all():
            counts[status_enum.value] = count
        return counts
