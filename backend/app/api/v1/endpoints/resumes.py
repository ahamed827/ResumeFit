import uuid

from app.api.deps import get_current_user
from app.core.rate_limiter import rate_limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.resume import ResumeListResponse, ResumeResponse, ResumeUpdate
from app.services.resume_service import ResumeService
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Rate limit: 10 uploads per hour per user
    await rate_limiter.check_rate_limit(
        f"rate:resume_upload:{current_user.id}", max_requests=10, window_seconds=3600
    )

    service = ResumeService(db)
    return await service.upload_and_process(current_user.id, file)


@router.get("", response_model=ResumeListResponse, status_code=status.HTTP_200_OK)
async def list_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    items, total = await service.list_resumes(current_user.id, skip=skip, limit=limit)
    return ResumeListResponse(items=items, total=total, page=(skip // limit) + 1, size=limit)


@router.get("/{resume_id}", response_model=ResumeResponse, status_code=status.HTTP_200_OK)
async def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    return await service.get_resume(resume_id, current_user.id)


@router.patch("/{resume_id}", response_model=ResumeResponse, status_code=status.HTTP_200_OK)
async def update_resume_profile(
    resume_id: uuid.UUID,
    update_data: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    return await service.update_resume(resume_id, current_user.id, update_data)


@router.delete("/{resume_id}", status_code=status.HTTP_200_OK)
async def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    await service.delete_resume(resume_id, current_user.id)
    return {"message": "Resume and associated data successfully removed."}


@router.post("/{resume_id}/reparse", response_model=ResumeResponse, status_code=status.HTTP_200_OK)
async def reparse_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    return await service.reparse_resume(resume_id, current_user.id)
