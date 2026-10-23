import enum
import uuid
from typing import Any, Dict, Optional

from app.db.base import Base, TimestampMixin
from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

JSONType = JSON().with_variant(JSONB, "postgresql")


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Match(Base, TimestampMixin):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )

    overall_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True, index=True)
    component_scores: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    matched_skills: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    missing_skills: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    partial_skills: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    evidence: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    improvement_plan: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    prompt_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus, name="match_status_enum", native_enum=False),
        default=MatchStatus.PENDING,
        nullable=False,
        index=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="matches")
    resume: Mapped["Resume"] = relationship("Resume", back_populates="matches")
    job: Mapped["Job"] = relationship("Job", back_populates="matches")
