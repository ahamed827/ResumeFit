import uuid
from typing import Optional

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.job import JobCreate, JobListResponse, JobResponse, JobUpdate
from app.services.job_service import JobService
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    return await service.create_job(current_user.id, job_data)


@router.post("/upload", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def upload_job_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    return await service.create_job_from_file(current_user.id, file)


@router.get("", response_model=JobListResponse, status_code=status.HTTP_200_OK)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    items, total = await service.list_jobs(current_user.id, skip=skip, limit=limit, search=search)
    return JobListResponse(items=items, total=total, page=(skip // limit) + 1, size=limit)


@router.get("/{job_id}", response_model=JobResponse, status_code=status.HTTP_200_OK)
async def get_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    return await service.get_job(job_id, current_user.id)


@router.patch("/{job_id}", response_model=JobResponse, status_code=status.HTTP_200_OK)
async def update_job(
    job_id: uuid.UUID,
    update_data: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    return await service.update_job(job_id, current_user.id, update_data)


@router.delete("/{job_id}", status_code=status.HTTP_200_OK)
async def delete_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    await service.delete_job(job_id, current_user.id)
    return {"message": "Job description removed successfully."}


@router.post("/{job_id}/analyze", response_model=JobResponse, status_code=status.HTTP_200_OK)
async def analyze_job(
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    return await service.reanalyze_job(job_id, current_user.id)
