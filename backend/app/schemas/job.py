import uuid
from datetime import datetime
from typing import List, Optional

from app.models.job import AnalysisStatus, JobSourceType
from pydantic import BaseModel, ConfigDict, Field


class StructuredJobRequirements(BaseModel):
    job_title: str = ""
    company_name: Optional[str] = None
    seniority_level: Optional[str] = "Entry / Mid Level"
    employment_type: Optional[str] = "Full-time"
    location: Optional[str] = None
    must_have_skills: List[str] = Field(default_factory=list)
    nice_to_have_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    experience_requirements: Optional[str] = None
    years_of_experience: Optional[float] = None
    keywords: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)


class JobCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    company_name: Optional[str] = None
    raw_description: str = Field(..., min_length=20)


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company_name: Optional[str] = None
    structured_requirements: Optional[StructuredJobRequirements] = None


class JobResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    company_name: Optional[str] = None
    source_type: JobSourceType
    raw_description: str
    file_url: Optional[str] = None
    structured_requirements: Optional[StructuredJobRequirements] = None
    analysis_status: AnalysisStatus
    parsing_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    size: int
