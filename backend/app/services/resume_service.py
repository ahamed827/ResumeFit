import json
import uuid
from pathlib import Path
from typing import List, Tuple

from app.core.errors import BadRequestError, NotFoundError
from app.core.logging import logger
from app.integrations.document_parser import document_parser
from app.integrations.llm_service import llm_service
from app.integrations.storage_service import storage_service
from app.models.audit import AILogStatus, AITaskType
from app.models.resume import ExtractionStatus, Resume
from app.repositories.audit_repository import AuditRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.resume import ResumeResponse, ResumeUpdate, StructuredResumeProfile
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession


class ResumeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.resume_repo = ResumeRepository(db)
        self.audit_repo = AuditRepository(db)

    async def upload_and_process(
        self, user_id: uuid.UUID, upload_file: UploadFile
    ) -> ResumeResponse:
        """Saves resume file, extracts text, and parses into structured profile."""
        filename = upload_file.filename or "resume.pdf"
        file_url, local_path_str, file_size, mime_type = await storage_service.save_file(
            upload_file
        )

        # Stage 1: Document extraction
        try:
            local_path = Path(local_path_str)
            raw_text = document_parser.extract_text(local_path, filename)
        except Exception as e:
            logger.error(f"Text extraction failed for {filename}: {e}")
            resume = await self.resume_repo.create(
                user_id=user_id,
                original_filename=filename,
                file_url=file_url,
                file_size_bytes=file_size,
                mime_type=mime_type,
                raw_text=None,
                extraction_status=ExtractionStatus.FAILED,
            )
            await self.resume_repo.update(resume, parsing_error=str(e))
            return ResumeResponse.model_validate(resume)

        # Create record in DB as PROCESSING
        resume = await self.resume_repo.create(
            user_id=user_id,
            original_filename=filename,
            file_url=file_url,
            file_size_bytes=file_size,
            mime_type=mime_type,
            raw_text=raw_text,
            extraction_status=ExtractionStatus.PROCESSING,
        )

        # Stage 2: Resume structuring via LLM
        await self._parse_structured_profile(resume, raw_text, user_id)
        return ResumeResponse.model_validate(resume)

    async def _parse_structured_profile(
        self, resume: Resume, raw_text: str, user_id: uuid.UUID
    ) -> None:
        """Parses extracted raw text into structured JSON matching StructuredResumeProfile."""
        prompt_path = Path("prompts/resume_extraction_v1.json")
        system_prompt = "You are an expert resume parsing system. Extract structured info matching the schema strictly."
        user_template = 'Resume Text:\n"""\n{text}\n"""\n\nExtract and return the structured profile adhering strictly to the JSON schema.'

        if prompt_path.exists():
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    p_data = json.load(f)
                    system_prompt = p_data.get("system_prompt", system_prompt)
                    user_template = p_data.get("user_template", user_template)
            except Exception:
                pass

        user_prompt = user_template.replace("{text}", raw_text[:6000])

        try:
            (
                structured_profile,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                cost,
                latency,
                model_name,
            ) = await llm_service.call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=StructuredResumeProfile,
                task_name="resume_extraction",
            )

            await self.resume_repo.update(
                resume,
                structured_profile=structured_profile.model_dump(),
                extraction_status=ExtractionStatus.COMPLETED,
                parsing_error=None,
            )

            await self.audit_repo.log_ai_usage(
                task_type=AITaskType.RESUME_EXTRACTION,
                model_name=model_name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=cost,
                latency_ms=latency,
                status=AILogStatus.SUCCESS,
                user_id=user_id,
            )

        except Exception as e:
            logger.error(f"Failed to structure resume profile for ID {resume.id}: {e}")
            await self.resume_repo.update(
                resume,
                extraction_status=ExtractionStatus.FAILED,
                parsing_error=f"Structuring failed: {str(e)}",
            )
            await self.audit_repo.log_ai_usage(
                task_type=AITaskType.RESUME_EXTRACTION,
                model_name="failed",
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                estimated_cost_usd=0.0,
                latency_ms=0,
                status=AILogStatus.FAILED,
                user_id=user_id,
                error_message=str(e),
            )

    async def get_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> ResumeResponse:
        resume = await self.resume_repo.get_by_id_and_user(resume_id, user_id)
        if not resume:
            raise NotFoundError("Resume", resume_id)
        return ResumeResponse.model_validate(resume)

    async def list_resumes(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> Tuple[List[ResumeResponse], int]:
        items, total = await self.resume_repo.list_by_user(user_id, skip=skip, limit=limit)
        return [ResumeResponse.model_validate(r) for r in items], total

    async def update_resume(
        self, resume_id: uuid.UUID, user_id: uuid.UUID, update_data: ResumeUpdate
    ) -> ResumeResponse:
        resume = await self.resume_repo.get_by_id_and_user(resume_id, user_id)
        if not resume:
            raise NotFoundError("Resume", resume_id)

        await self.resume_repo.update(
            resume, structured_profile=update_data.structured_profile.model_dump()
        )
        return ResumeResponse.model_validate(resume)

    async def delete_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        resume = await self.resume_repo.get_by_id_and_user(resume_id, user_id)
        if not resume:
            raise NotFoundError("Resume", resume_id)

        storage_service.delete_file(resume.file_url)
        await self.resume_repo.soft_delete(resume)
        return True

    async def reparse_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> ResumeResponse:
        resume = await self.resume_repo.get_by_id_and_user(resume_id, user_id)
        if not resume:
            raise NotFoundError("Resume", resume_id)

        raw_text = resume.raw_text
        if not raw_text:
            local_path = storage_service.get_local_path(resume.file_url)
            if local_path and local_path.exists():
                raw_text = document_parser.extract_text(local_path, resume.original_filename)
                await self.resume_repo.update(resume, raw_text=raw_text)
            else:
                raise BadRequestError("Original file is no longer available on disk to re-extract.")

        await self.resume_repo.update(
            resume, extraction_status=ExtractionStatus.PROCESSING, parsing_error=None
        )
        await self._parse_structured_profile(resume, raw_text, user_id)
        return ResumeResponse.model_validate(resume)
