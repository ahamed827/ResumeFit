import uuid

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.summary import SummaryGenerateRequest, SummaryListResponse, SummaryResponse
from app.services.summary_service import SummaryService
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/summaries", tags=["Resume Summaries"])


@router.post("", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
async def generate_summary(
    req: SummaryGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SummaryService(db)
    return await service.generate_tailored_summary(current_user.id, req)


@router.get("", response_model=SummaryListResponse, status_code=status.HTTP_200_OK)
async def list_summaries(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SummaryService(db)
    items, total = await service.list_summaries(current_user.id, skip=skip, limit=limit)
    return SummaryListResponse(items=items, total=total)


@router.get("/{summary_id}", response_model=SummaryResponse, status_code=status.HTTP_200_OK)
async def get_summary(
    summary_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SummaryService(db)
    return await service.get_summary(summary_id, current_user.id)
