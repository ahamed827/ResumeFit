import uuid
from typing import List, Optional, Tuple

from app.models.resume import ExtractionStatus, Resume
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


class ResumeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, resume_id: uuid.UUID) -> Optional[Resume]:
        stmt = select(Resume).where(Resume.id == resume_id, Resume.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_id_and_user(
        self, resume_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Resume]:
        stmt = select(Resume).where(
            Resume.id == resume_id, Resume.user_id == user_id, Resume.deleted_at.is_(None)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> Tuple[List[Resume], int]:
        total_stmt = select(func.count(Resume.id)).where(
            Resume.user_id == user_id, Resume.deleted_at.is_(None)
        )
        total_res = await self.db.execute(total_stmt)
        total = total_res.scalar_one()

        stmt = (
            select(Resume)
            .where(Resume.user_id == user_id, Resume.deleted_at.is_(None))
            .order_by(Resume.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all()), total

    async def create(
        self,
        user_id: uuid.UUID,
        original_filename: str,
        file_url: str,
        file_size_bytes: int,
        mime_type: str,
        raw_text: Optional[str] = None,
        extraction_status: ExtractionStatus = ExtractionStatus.PENDING,
    ) -> Resume:
        resume = Resume(
            id=uuid.uuid4(),
            user_id=user_id,
            original_filename=original_filename,
            file_url=file_url,
            file_size_bytes=file_size_bytes,
            mime_type=mime_type,
            raw_text=raw_text,
            extraction_status=extraction_status,
        )
        self.db.add(resume)
        await self.db.flush()
        return resume

    async def update(self, resume: Resume, **kwargs) -> Resume:
        for key, value in kwargs.items():
            if hasattr(resume, key):
                setattr(resume, key, value)
        await self.db.flush()
        return resume

    async def soft_delete(self, resume: Resume) -> None:
        resume.soft_delete()
        await self.db.flush()

    async def count_all_completed(self) -> int:
        stmt = select(func.count(Resume.id)).where(
            Resume.extraction_status == ExtractionStatus.COMPLETED, Resume.deleted_at.is_(None)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one()
