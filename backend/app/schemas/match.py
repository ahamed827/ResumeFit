import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.match import MatchStatus
from pydantic import BaseModel, ConfigDict, Field


class ComponentScores(BaseModel):
    required_skills: float = Field(..., ge=0.0, le=100.0)
    experience_relevance: float = Field(..., ge=0.0, le=100.0)
    nice_to_have_skills: float = Field(..., ge=0.0, le=100.0)
    projects_and_practical: float = Field(..., ge=0.0, le=100.0)
    education_fit: float = Field(..., ge=0.0, le=100.0)
    seniority_alignment: float = Field(..., ge=0.0, le=100.0)


class MatchedSkillDetail(BaseModel):
    skill: str
    resume_evidence: str
    confidence: float = 1.0
    category: Optional[str] = "required"


class MissingSkillDetail(BaseModel):
    skill: str
    importance: str = "critical"  # "critical", "important", "nice_to_have"
    category: Optional[str] = None


class PartialSkillDetail(BaseModel):
    skill: str
    related_resume_skill: str
    explanation: str


class ProjectIdea(BaseModel):
    title: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    key_features: List[str] = Field(default_factory=list)


class LearningResource(BaseModel):
    topic: str
    resource_name: str
    resource_type: str  # "Documentation", "Course", "Tutorial", "Book"
    url: Optional[str] = None


class ImprovementPlan(BaseModel):
    missing_skills_ranked: List[MissingSkillDetail] = Field(default_factory=list)
    learning_resources: List[LearningResource] = Field(default_factory=list)
    project_ideas: List[ProjectIdea] = Field(default_factory=list)
    resume_improvements: List[str] = Field(default_factory=list)
    interview_topics: List[str] = Field(default_factory=list)


class MatchCreateRequest(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID


class MatchResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    resume_id: uuid.UUID
    job_id: uuid.UUID
    overall_score: Optional[float] = None
    component_scores: Optional[ComponentScores] = None
    matched_skills: List[MatchedSkillDetail] = Field(default_factory=list)
    missing_skills: List[MissingSkillDetail] = Field(default_factory=list)
    partial_skills: List[PartialSkillDetail] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    explanation: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    improvement_plan: Optional[ImprovementPlan] = None
    model_name: Optional[str] = None
    prompt_version: Optional[str] = None
    status: MatchStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchListResponse(BaseModel):
    items: List[MatchResponse]
    total: int
    page: int
    size: int
