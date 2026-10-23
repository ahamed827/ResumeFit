import uuid
from typing import List, Optional, Tuple

from app.core.errors import NotFoundError
from app.models.application import ApplicationStatus
from app.repositories.application_repository import ApplicationRepository
from app.repositories.job_repository import JobRepository
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationStatsResponse,
    ApplicationUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession


class ApplicationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.app_repo = ApplicationRepository(db)
        self.job_repo = JobRepository(db)

    async def create_application(
        self, user_id: uuid.UUID, req: ApplicationCreate
    ) -> ApplicationResponse:
        job = await self.job_repo.get_by_id_and_user(req.job_id, user_id)
        if not job:
            raise NotFoundError("Job", req.job_id)

        app_obj = await self.app_repo.create(
            user_id=user_id,
            job_id=req.job_id,
            resume_id=req.resume_id,
            status=req.status,
            applied_at=req.applied_at,
            deadline=req.deadline,
            notes=req.notes,
        )
        # Fetch fresh with job relation loaded
        loaded_app = await self.app_repo.get_by_id(app_obj.id)
        return ApplicationResponse.model_validate(loaded_app)

    async def get_application(
        self, application_id: uuid.UUID, user_id: uuid.UUID
    ) -> ApplicationResponse:
        app_obj = await self.app_repo.get_by_id_and_user(application_id, user_id)
        if not app_obj:
            raise NotFoundError("Application", application_id)
        return ApplicationResponse.model_validate(app_obj)

    async def list_applications(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        status: Optional[ApplicationStatus] = None,
        search: Optional[str] = None,
    ) -> Tuple[List[ApplicationResponse], int]:
        items, total = await self.app_repo.list_by_user(
            user_id=user_id, skip=skip, limit=limit, status=status, search=search
        )
        return [ApplicationResponse.model_validate(a) for a in items], total

    async def update_application(
        self, application_id: uuid.UUID, user_id: uuid.UUID, update_data: ApplicationUpdate
    ) -> ApplicationResponse:
        app_obj = await self.app_repo.get_by_id_and_user(application_id, user_id)
        if not app_obj:
            raise NotFoundError("Application", application_id)

        update_dict = {}
        if update_data.status is not None:
            update_dict["status"] = update_data.status
        if update_data.applied_at is not None:
            update_dict["applied_at"] = update_data.applied_at
        if update_data.deadline is not None:
            update_dict["deadline"] = update_data.deadline
        if update_data.notes is not None:
            update_dict["notes"] = update_data.notes
        if update_data.resume_id is not None:
            update_dict["resume_id"] = update_data.resume_id

        await self.app_repo.update(app_obj, **update_dict)
        refreshed = await self.app_repo.get_by_id(app_obj.id)
        return ApplicationResponse.model_validate(refreshed)

    async def delete_application(self, application_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        app_obj = await self.app_repo.get_by_id_and_user(application_id, user_id)
        if not app_obj:
            raise NotFoundError("Application", application_id)
        await self.app_repo.delete(app_obj)
        return True

    async def get_stats(self, user_id: uuid.UUID) -> ApplicationStatsResponse:
        counts = await self.app_repo.get_status_counts(user_id)
        total = sum(counts.values())
        return ApplicationStatsResponse(
            total_applications=total, by_status=counts, recent_activity_count=total
        )
