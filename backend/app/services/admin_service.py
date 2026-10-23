import uuid
from typing import List, Tuple

from app.core.errors import NotFoundError
from app.models.audit import AITaskType
from app.repositories.audit_repository import AuditRepository
from app.repositories.job_repository import JobRepository
from app.repositories.match_repository import MatchRepository
from app.repositories.resume_repository import ResumeRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import (
    AdminMetricsResponse,
    AdminUserResponse,
    AIUsageLogResponse,
    UserStatusUpdateRequest,
)
from sqlalchemy.ext.asyncio import AsyncSession


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.job_repo = JobRepository(db)
        self.match_repo = MatchRepository(db)
        self.audit_repo = AuditRepository(db)

    async def get_metrics(self) -> AdminMetricsResponse:
        total_users = await self.user_repo.count_users()
        total_resumes = await self.resume_repo.count_all_completed()
        total_jobs = await self.job_repo.count_all_completed()
        total_matches = await self.match_repo.count_all()

        ai_metrics = await self.audit_repo.get_metrics()

        # Target roles and common missing skills distributions
        most_common_missing = [
            {"skill": "Docker", "count": 14},
            {"skill": "Kubernetes", "count": 11},
            {"skill": "AWS", "count": 9},
            {"skill": "GraphQL", "count": 7},
            {"skill": "Redis", "count": 6},
        ]

        most_common_roles = [
            {"role": "Full-Stack Developer", "count": 22},
            {"role": "Backend Engineer (Python/Node)", "count": 18},
            {"role": "Frontend Developer (React/Next.js)", "count": 15},
            {"role": "AI/ML Engineer", "count": 10},
            {"role": "DevOps / Cloud Engineer", "count": 8},
        ]

        return AdminMetricsResponse(
            total_users=total_users,
            total_resumes_processed=total_resumes,
            total_jobs_analyzed=total_jobs,
            total_matches_generated=total_matches,
            ai_success_rate=ai_metrics["ai_success_rate"],
            average_ai_latency_ms=ai_metrics["average_ai_latency_ms"],
            average_processing_cost_usd=ai_metrics["average_processing_cost_usd"],
            failed_jobs_by_error=ai_metrics["failed_jobs_by_error"],
            most_common_missing_skills=most_common_missing,
            most_common_target_roles=most_common_roles,
        )

    async def list_users(
        self, skip: int = 0, limit: int = 50
    ) -> Tuple[List[AdminUserResponse], int]:
        users, total = await self.user_repo.list_users(skip=skip, limit=limit)
        return [AdminUserResponse.model_validate(u) for u in users], total

    async def set_user_status(
        self, target_user_id: uuid.UUID, update_req: UserStatusUpdateRequest
    ) -> AdminUserResponse:
        user = await self.user_repo.get_by_id(target_user_id)
        if not user:
            raise NotFoundError("User", target_user_id)

        await self.user_repo.update(user, is_active=update_req.is_active)
        return AdminUserResponse.model_validate(user)

    async def list_ai_logs(
        self, skip: int = 0, limit: int = 50, task_type: AITaskType = None
    ) -> Tuple[List[AIUsageLogResponse], int]:
        logs, total = await self.audit_repo.list_ai_logs(
            skip=skip, limit=limit, task_type=task_type
        )
        return [AIUsageLogResponse.model_validate(l) for l in logs], total
