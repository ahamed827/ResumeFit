import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.models.application import ApplicationStatus
from app.schemas.job import JobResponse
from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    job_id: uuid.UUID
    resume_id: Optional[uuid.UUID] = None
    status: ApplicationStatus = ApplicationStatus.SAVED
    applied_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    applied_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None
    resume_id: Optional[uuid.UUID] = None


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    resume_id: Optional[uuid.UUID] = None
    status: ApplicationStatus
    applied_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    job: Optional[JobResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ApplicationStatsResponse(BaseModel):
    total_applications: int
    by_status: Dict[str, int]
    recent_activity_count: int


class ApplicationListResponse(BaseModel):
    items: List[ApplicationResponse]
    total: int
    page: int
    size: int
