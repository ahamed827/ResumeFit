import uuid
from typing import Optional

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.audit import AITaskType
from app.models.user import User
from app.schemas.admin import (
    AdminMetricsResponse,
    AdminUserResponse,
    AIUsageListResponse,
    UserStatusUpdateRequest,
)
from app.services.admin_service import AdminService
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/metrics", response_model=AdminMetricsResponse, status_code=status.HTTP_200_OK)
async def get_admin_metrics(
    admin_user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    service = AdminService(db)
    return await service.get_metrics()


@router.get("/ai-usage", response_model=AIUsageListResponse, status_code=status.HTTP_200_OK)
async def get_ai_usage_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    task_type: Optional[AITaskType] = Query(None),
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    items, total = await service.list_ai_logs(skip=skip, limit=limit, task_type=task_type)
    return AIUsageListResponse(items=items, total=total, page=(skip // limit) + 1, size=limit)


@router.get("/users", status_code=status.HTTP_200_OK)
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    users, total = await service.list_users(skip=skip, limit=limit)
    return {"items": users, "total": total, "page": (skip // limit) + 1, "size": limit}


@router.patch(
    "/users/{user_id}/status", response_model=AdminUserResponse, status_code=status.HTTP_200_OK
)
async def update_user_status(
    user_id: uuid.UUID,
    update_req: UserStatusUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdminService(db)
    return await service.set_user_status(user_id, update_req)
