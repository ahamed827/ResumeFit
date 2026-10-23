import enum
import uuid
from typing import Any, Dict, List, Optional

from app.db.base import Base, SoftDeleteMixin, TimestampMixin
from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class ExtractionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Fallback to JSON if not Postgres (e.g. SQLite tests)
JSONType = JSON().with_variant(JSONB, "postgresql")


class Resume(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    extraction_status: Mapped[ExtractionStatus] = mapped_column(
        Enum(ExtractionStatus, name="extraction_status_enum", native_enum=False),
        default=ExtractionStatus.PENDING,
        nullable=False,
        index=True,
    )
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    structured_profile: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    parsing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="resumes")
    matches: Mapped[List["Match"]] = relationship(
        "Match", back_populates="resume", cascade="all, delete-orphan"
    )
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="resume")
