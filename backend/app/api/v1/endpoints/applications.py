import uuid
from typing import Optional

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.application import ApplicationStatus
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationListResponse,
    ApplicationResponse,
    ApplicationStatsResponse,
    ApplicationUpdate,
)
from app.services.application_service import ApplicationService
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("/stats", response_model=ApplicationStatsResponse, status_code=status.HTTP_200_OK)
async def get_application_stats(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    service = ApplicationService(db)
    return await service.get_stats(current_user.id)


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    req: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    return await service.create_application(current_user.id, req)


@router.get("", response_model=ApplicationListResponse, status_code=status.HTTP_200_OK)
async def list_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[ApplicationStatus] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    items, total = await service.list_applications(
        current_user.id, skip=skip, limit=limit, status=status, search=search
    )
    return ApplicationListResponse(items=items, total=total, page=(skip // limit) + 1, size=limit)


@router.get("/{application_id}", response_model=ApplicationResponse, status_code=status.HTTP_200_OK)
async def get_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    return await service.get_application(application_id, current_user.id)


@router.patch(
    "/{application_id}", response_model=ApplicationResponse, status_code=status.HTTP_200_OK
)
async def update_application(
    application_id: uuid.UUID,
    update_data: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    return await service.update_application(application_id, current_user.id, update_data)


@router.delete("/{application_id}", status_code=status.HTTP_200_OK)
async def delete_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    await service.delete_application(application_id, current_user.id)
    return {"message": "Application removed from tracker."}
