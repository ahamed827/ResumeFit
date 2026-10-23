import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.models.audit import AILogStatus, AITaskType
from app.models.user import UserRole
from pydantic import BaseModel, ConfigDict


class UserStatusUpdateRequest(BaseModel):
    is_active: bool


class AdminUserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    email_verified: bool
    created_at: datetime
    resumes_count: int = 0
    matches_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class AdminMetricsResponse(BaseModel):
    total_users: int
    total_resumes_processed: int
    total_jobs_analyzed: int
    total_matches_generated: int
    ai_success_rate: float
    average_ai_latency_ms: float
    average_processing_cost_usd: float
    failed_jobs_by_error: Dict[str, int]
    most_common_missing_skills: List[Dict[str, int]]
    most_common_target_roles: List[Dict[str, int]]


class AIUsageLogResponse(BaseModel):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    task_type: AITaskType
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    latency_ms: int
    status: AILogStatus
    error_message: Optional[str] = None
    request_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIUsageListResponse(BaseModel):
    items: List[AIUsageLogResponse]
    total: int
    page: int
    size: int
