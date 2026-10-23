import json
import uuid
from pathlib import Path
from typing import List, Optional, Tuple

from app.core.errors import NotFoundError
from app.core.logging import logger
from app.integrations.document_parser import document_parser
from app.integrations.llm_service import llm_service
from app.integrations.storage_service import storage_service
from app.models.audit import AILogStatus, AITaskType
from app.models.job import AnalysisStatus, Job, JobSourceType
from app.repositories.audit_repository import AuditRepository
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobCreate, JobResponse, JobUpdate, StructuredJobRequirements
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
        self.audit_repo = AuditRepository(db)

    async def create_job(self, user_id: uuid.UUID, job_data: JobCreate) -> JobResponse:
        """Create a job from pasted text and triggers analysis."""
        job = await self.job_repo.create(
            user_id=user_id,
            title=job_data.title,
            company_name=job_data.company_name,
            raw_description=job_data.raw_description,
            source_type=JobSourceType.PASTED,
            analysis_status=AnalysisStatus.PROCESSING,
        )
        await self._analyze_job(job, job.raw_description, user_id)
        return JobResponse.model_validate(job)

    async def create_job_from_file(
        self, user_id: uuid.UUID, upload_file: UploadFile
    ) -> JobResponse:
        """Create a job from uploaded TXT/PDF/DOCX file and trigger analysis."""
        filename = upload_file.filename or "job_posting.txt"
        file_url, local_path_str, file_size, mime_type = await storage_service.save_file(
            upload_file
        )

        try:
            local_path = Path(local_path_str)
            raw_text = document_parser.extract_text(local_path, filename)
        except Exception as e:
            logger.error(f"Failed to read job file {filename}: {e}")
            job = await self.job_repo.create(
                user_id=user_id,
                title=Path(filename).stem,
                raw_description="Extraction failed.",
                source_type=JobSourceType.UPLOADED,
                file_url=file_url,
                analysis_status=AnalysisStatus.FAILED,
            )
            await self.job_repo.update(job, parsing_error=str(e))
            return JobResponse.model_validate(job)

        first_line = raw_text.split("\n")[0][:100].strip() or Path(filename).stem
        job = await self.job_repo.create(
            user_id=user_id,
            title=first_line,
            raw_description=raw_text,
            source_type=JobSourceType.UPLOADED,
            file_url=file_url,
            analysis_status=AnalysisStatus.PROCESSING,
        )

        await self._analyze_job(job, raw_text, user_id)
        return JobResponse.model_validate(job)

    async def _analyze_job(self, job: Job, raw_text: str, user_id: uuid.UUID) -> None:
        """Parses job description into structured requirements matching StructuredJobRequirements."""
        prompt_path = Path("prompts/job_extraction_v1.json")
        system_prompt = "You are a professional technical recruiter and job specification parser. Extract structured requirements matching the schema strictly."
        user_template = 'Job Description Text:\n"""\n{text}\n"""\n\nExtract and return the structured job requirements matching the specified JSON schema.'

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
                structured_reqs,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                cost,
                latency,
                model_name,
            ) = await llm_service.call_llm(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                schema=StructuredJobRequirements,
                task_name="job_extraction",
            )

            # Update job title and company if parsed cleanly, retaining user-provided title if present
            new_title = (
                job.title
                if job.title and job.title != "Software Engineer"
                else (structured_reqs.job_title or job.title)
            )
            new_company = (
                structured_reqs.company_name if structured_reqs.company_name else job.company_name
            )

            await self.job_repo.update(
                job,
                title=new_title,
                company_name=new_company,
                structured_requirements=structured_reqs.model_dump(),
                analysis_status=AnalysisStatus.COMPLETED,
                parsing_error=None,
            )

            await self.audit_repo.log_ai_usage(
                task_type=AITaskType.JOB_EXTRACTION,
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
            logger.error(f"Failed to analyze job requirements for ID {job.id}: {e}")
            await self.job_repo.update(
                job,
                analysis_status=AnalysisStatus.FAILED,
                parsing_error=f"Job analysis failed: {str(e)}",
            )
            await self.audit_repo.log_ai_usage(
                task_type=AITaskType.JOB_EXTRACTION,
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

    async def get_job(self, job_id: uuid.UUID, user_id: uuid.UUID) -> JobResponse:
        job = await self.job_repo.get_by_id_and_user(job_id, user_id)
        if not job:
            raise NotFoundError("Job", job_id)
        return JobResponse.model_validate(job)

    async def list_jobs(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20, search: Optional[str] = None
    ) -> Tuple[List[JobResponse], int]:
        items, total = await self.job_repo.list_by_user(
            user_id, skip=skip, limit=limit, search=search
        )
        return [JobResponse.model_validate(j) for j in items], total

    async def update_job(
        self, job_id: uuid.UUID, user_id: uuid.UUID, update_data: JobUpdate
    ) -> JobResponse:
        job = await self.job_repo.get_by_id_and_user(job_id, user_id)
        if not job:
            raise NotFoundError("Job", job_id)

        update_fields = {}
        if update_data.title is not None:
            update_fields["title"] = update_data.title
        if update_data.company_name is not None:
            update_fields["company_name"] = update_data.company_name
        if update_data.structured_requirements is not None:
            update_fields["structured_requirements"] = (
                update_data.structured_requirements.model_dump()
            )

        await self.job_repo.update(job, **update_fields)
        return JobResponse.model_validate(job)

    async def delete_job(self, job_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        job = await self.job_repo.get_by_id_and_user(job_id, user_id)
        if not job:
            raise NotFoundError("Job", job_id)

        if job.file_url:
            storage_service.delete_file(job.file_url)

        await self.job_repo.soft_delete(job)
        return True

    async def reanalyze_job(self, job_id: uuid.UUID, user_id: uuid.UUID) -> JobResponse:
        job = await self.job_repo.get_by_id_and_user(job_id, user_id)
        if not job:
            raise NotFoundError("Job", job_id)

        await self.job_repo.update(
            job, analysis_status=AnalysisStatus.PROCESSING, parsing_error=None
        )
        await self._analyze_job(job, job.raw_description, user_id)
        return JobResponse.model_validate(job)
