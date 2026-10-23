import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SummaryGenerateRequest(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID


class SummaryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    resume_id: uuid.UUID
    job_id: uuid.UUID
    generated_summary: str
    supported_evidence: List[str] = []
    unsupported_flags: List[str] = []
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SummaryListResponse(BaseModel):
    items: List[SummaryResponse]
    total: int
