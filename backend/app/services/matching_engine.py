import uuid
from typing import Any, Dict, List, Tuple

from app.core.config import settings
from app.core.errors import BadRequestError, NotFoundError
from app.core.logging import logger
from app.integrations.embedding_service import embedding_service
from app.models.audit import AILogStatus, AITaskType
from app.models.job import AnalysisStatus
from app.models.match import Match, MatchStatus
from app.models.resume import ExtractionStatus
from app.repositories.audit_repository import AuditRepository
from app.repositories.job_repository import JobRepository
from app.repositories.match_repository import MatchRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.match import (
    ComponentScores,
    ImprovementPlan,
    MatchedSkillDetail,
    MatchResponse,
    MissingSkillDetail,
    PartialSkillDetail,
)
from sqlalchemy.ext.asyncio import AsyncSession


class MatchingEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.match_repo = MatchRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.job_repo = JobRepository(db)
        self.audit_repo = AuditRepository(db)

    async def create_and_run_match(
        self, user_id: uuid.UUID, resume_id: uuid.UUID, job_id: uuid.UUID
    ) -> MatchResponse:
        resume = await self.resume_repo.get_by_id_and_user(resume_id, user_id)
        if not resume:
            raise NotFoundError("Resume", resume_id)

        job = await self.job_repo.get_by_id_and_user(job_id, user_id)
        if not job:
            raise NotFoundError("Job", job_id)

        if resume.extraction_status != ExtractionStatus.COMPLETED or not resume.structured_profile:
            raise BadRequestError("Resume must be successfully parsed before matching can run.")

        if job.analysis_status != AnalysisStatus.COMPLETED or not job.structured_requirements:
            raise BadRequestError("Job must be successfully analyzed before matching can run.")

        # Check existing match or create new
        existing_match = await self.match_repo.get_by_resume_and_job(resume_id, job_id)
        if existing_match:
            match_obj = existing_match
            await self.match_repo.update(
                match_obj, status=MatchStatus.PROCESSING, error_message=None
            )
        else:
            match_obj = await self.match_repo.create(
                user_id=user_id, resume_id=resume_id, job_id=job_id, status=MatchStatus.PROCESSING
            )

        try:
            match_result = await self._execute_matching_pipeline(
                resume.structured_profile,
                job.structured_requirements,
                resume.raw_text or "",
                job.raw_description or "",
            )

            await self.match_repo.update(
                match_obj,
                overall_score=match_result["overall_score"],
                component_scores=match_result["component_scores"],
                matched_skills=match_result["matched_skills"],
                missing_skills=match_result["missing_skills"],
                partial_skills=match_result["partial_skills"],
                evidence=match_result["evidence"],
                explanation=match_result["explanation"],
                improvement_plan=match_result["improvement_plan"],
                model_name=match_result.get("model_name", "deterministic-engine-v1"),
                prompt_version="1.0.0",
                status=MatchStatus.COMPLETED,
                error_message=None,
            )

            await self.audit_repo.log_ai_usage(
                task_type=AITaskType.MATCHING,
                model_name=match_result.get("model_name", "deterministic-engine-v1"),
                prompt_tokens=match_result.get("prompt_tokens", 250),
                completion_tokens=match_result.get("completion_tokens", 350),
                total_tokens=match_result.get("total_tokens", 600),
                estimated_cost_usd=match_result.get("cost", 0.0001),
                latency_ms=match_result.get("latency_ms", 120),
                status=AILogStatus.SUCCESS,
                user_id=user_id,
            )

        except Exception as e:
            logger.error(f"Matching pipeline failed for match {match_obj.id}: {e}")
            await self.match_repo.update(
                match_obj,
                status=MatchStatus.FAILED,
                error_message=f"Matching calculation failed: {str(e)}",
            )
            await self.audit_repo.log_ai_usage(
                task_type=AITaskType.MATCHING,
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

        return self._format_match_response(match_obj)

    async def _execute_matching_pipeline(
        self,
        resume_profile: Dict[str, Any],
        job_reqs: Dict[str, Any],
        resume_raw: str,
        job_raw: str,
    ) -> Dict[str, Any]:
        """Calculates component scores and extracts evidence deterministically and explainably."""
        # 1. Collect resume skills from all sections
        resume_skills_set = set(resume_profile.get("skills", []))
        for exp in resume_profile.get("work_experience", []):
            resume_skills_set.update(exp.get("technologies_used", []))
        for proj in resume_profile.get("projects", []):
            resume_skills_set.update(proj.get("technologies_used", []))
        resume_skills = list(resume_skills_set)

        must_have = job_reqs.get("must_have_skills", [])
        nice_to_have = job_reqs.get("nice_to_have_skills", [])

        # 2. Stage 4: Semantic skill matching for required and nice-to-have skills
        must_match_res = await embedding_service.match_skills(resume_skills, must_have)
        nice_match_res = await embedding_service.match_skills(resume_skills, nice_to_have)

        # Matched skills list with evidence
        matched_skills_list: List[Dict[str, Any]] = []
        for m in must_match_res["matched"]:
            evidence_quote = self._find_evidence_quote(
                m["matched_with"], resume_raw, resume_profile
            )
            matched_skills_list.append(
                {
                    "skill": m["skill"],
                    "resume_evidence": evidence_quote,
                    "confidence": m.get("similarity", 1.0),
                    "category": "required",
                }
            )

        for m in nice_match_res["matched"]:
            evidence_quote = self._find_evidence_quote(
                m["matched_with"], resume_raw, resume_profile
            )
            matched_skills_list.append(
                {
                    "skill": m["skill"],
                    "resume_evidence": evidence_quote,
                    "confidence": m.get("similarity", 1.0),
                    "category": "preferred",
                }
            )

        # Missing skills classified: Critical for must-have, Nice-to-have for nice-to-have
        missing_skills_list: List[Dict[str, Any]] = []
        for s in must_match_res["missing"]:
            missing_skills_list.append(
                {"skill": s, "importance": "critical", "category": "must_have"}
            )
        for s in nice_match_res["missing"]:
            missing_skills_list.append(
                {"skill": s, "importance": "nice_to_have", "category": "nice_to_have"}
            )

        # Partial skills
        partial_skills_list = []
        for p in must_match_res["partial"] + nice_match_res["partial"]:
            partial_skills_list.append(
                {
                    "skill": p["skill"],
                    "related_resume_skill": p["related_resume_skill"],
                    "explanation": p["explanation"],
                }
            )

        # 3. Calculate Normalized Component Scores (0 to 100)
        # Component 1: Required Skills Score
        req_count = len(must_have)
        if req_count == 0:
            req_score = 100.0  # Job did not specify -> do not penalize
        else:
            matched_count = len(must_match_res["matched"])
            partial_count = len(must_match_res["partial"])
            req_score = min(100.0, ((matched_count + 0.5 * partial_count) / req_count) * 100.0)

        # Component 2: Nice-To-Have Skills Score
        nice_count = len(nice_to_have)
        if nice_count == 0:
            nice_score = 100.0
        else:
            nice_matched = len(nice_match_res["matched"])
            nice_score = min(100.0, (nice_matched / nice_count) * 100.0)

        # Component 3: Experience Relevance Score
        req_years = job_reqs.get("years_of_experience")
        work_history = resume_profile.get("work_experience", [])
        if req_years is None:
            exp_score = 90.0 if work_history else 80.0
        else:
            cand_years = len(work_history) * 1.0  # Approx 1 yr per listed role
            if cand_years >= req_years:
                exp_score = 100.0
            elif cand_years > 0:
                exp_score = max(40.0, (cand_years / req_years) * 100.0)
            else:
                exp_score = 50.0  # Fresher with project experience

        # Component 4: Projects and Practical Evidence Score
        projects = resume_profile.get("projects", [])
        if len(projects) >= 3:
            proj_score = 100.0
        elif len(projects) == 2:
            proj_score = 85.0
        elif len(projects) == 1:
            proj_score = 70.0
        else:
            proj_score = 40.0

        # Component 5: Education Fit Score
        edu_reqs = job_reqs.get("education_requirements", [])
        candidate_edu = resume_profile.get("education", [])
        if not edu_reqs or not edu_reqs[0]:
            edu_score = 100.0
        elif candidate_edu:
            # Check for CS / Software / STEM degree
            edu_str = " ".join(
                [f"{e.get('degree', '')} {e.get('field_of_study', '')}" for e in candidate_edu]
            ).lower()
            if any(
                term in edu_str
                for term in ["computer", "science", "engineering", "technology", "software"]
            ):
                edu_score = 100.0
            else:
                edu_score = 85.0
        else:
            edu_score = 65.0

        # Component 6: Seniority Alignment Score
        job_seniority = (job_reqs.get("seniority_level") or "Entry / Mid Level").lower()
        if "senior" in job_seniority or "lead" in job_seniority:
            sen_score = 60.0 if len(work_history) < 2 else 90.0
        else:
            sen_score = 95.0  # Entry / Junior / Mid role fits freshener profile well

        # 4. Compute Weighted Overall Score
        overall = (
            (req_score * settings.WEIGHT_REQUIRED_SKILLS)
            + (exp_score * settings.WEIGHT_EXPERIENCE)
            + (nice_score * settings.WEIGHT_NICE_TO_HAVE_SKILLS)
            + (proj_score * settings.WEIGHT_PROJECTS)
            + (edu_score * settings.WEIGHT_EDUCATION)
            + (sen_score * settings.WEIGHT_SENIORITY)
        )
        overall_score = round(min(100.0, max(0.0, overall)), 1)

        component_scores = {
            "required_skills": round(req_score, 1),
            "experience_relevance": round(exp_score, 1),
            "nice_to_have_skills": round(nice_score, 1),
            "projects_and_practical": round(proj_score, 1),
            "education_fit": round(edu_score, 1),
            "seniority_alignment": round(sen_score, 1),
        }

        # 5. Strengths, Risks & Explanation
        strengths = []
        if req_score >= 70:
            strengths.append(
                f"Strong alignment with core required technologies ({len(matched_skills_list)} skills matched)."
            )
        if proj_score >= 80:
            strengths.append(
                f"Solid portfolio demonstrating practical software engineering with {len(projects)} featured projects."
            )
        if edu_score >= 90:
            strengths.append(
                "Directly relevant academic background in Computer Science or Software Engineering."
            )
        if not strengths:
            strengths.append(
                "Demonstrated foundational technical competencies and transferable engineering skills."
            )

        risks = []
        if missing_skills_list:
            top_missing = [m["skill"] for m in missing_skills_list[:3]]
            risks.append(f"Gap in key required skills: {', '.join(top_missing)}.")
        if exp_score < 70 and req_years:
            risks.append(
                f"Position seeks {req_years}+ years of experience; candidate profile aligns closer to entry/fresher level."
            )

        explanation = (
            f"The candidate achieved an overall match score of {overall_score}/100. "
            f"They satisfy {round(req_score)}% of the core required technical stack with {len(matched_skills_list)} verified matches from their resume. "
            f"Their practical project and education credentials scored {round(proj_score)}% and {round(edu_score)}% respectively. "
            f"Closing gaps in {', '.join([m['skill'] for m in missing_skills_list[:2]]) or 'the remaining nice-to-have skills'} will make this profile highly competitive for this role."
        )

        # 6. Stage 6: Personalized Improvement Plan
        improvement_plan = self._generate_improvement_plan(
            missing_skills_list, job_reqs.get("job_title", "Software Engineer")
        )

        return {
            "overall_score": overall_score,
            "component_scores": component_scores,
            "matched_skills": matched_skills_list,
            "missing_skills": missing_skills_list,
            "partial_skills": partial_skills_list,
            "evidence": {
                "matched_count": len(matched_skills_list),
                "missing_count": len(missing_skills_list),
                "verified_quotes": [m["resume_evidence"] for m in matched_skills_list[:5]],
            },
            "explanation": explanation,
            "strengths": strengths,
            "risks": risks,
            "improvement_plan": improvement_plan,
        }

    def _find_evidence_quote(self, skill: str, raw_text: str, profile: Dict[str, Any]) -> str:
        """Finds an exact or closest quote mentioning the skill in the resume."""
        # Check projects first
        for proj in profile.get("projects", []):
            if skill.lower() in [t.lower() for t in proj.get("technologies_used", [])]:
                return f"Used in project '{proj.get('name', 'Portfolio')}': {proj.get('description', '')[:100]}"

        # Check work experience
        for exp in profile.get("work_experience", []):
            if skill.lower() in [t.lower() for t in exp.get("technologies_used", [])]:
                return f"Used at {exp.get('organization', 'Organization')} as {exp.get('title', 'Role')}."

        # Search in raw text line
        for line in raw_text.split("\n"):
            if skill.lower() in line.lower():
                clean_line = line.strip()
                if len(clean_line) > 10:
                    return clean_line[:120]

        return f"Listed under technical skills and proficiencies: {skill}."

    def _generate_improvement_plan(
        self, missing_skills: List[Dict[str, Any]], job_title: str
    ) -> Dict[str, Any]:
        """Generates targeted learning resources, practical project ideas, and interview prep topics."""
        ranked = sorted(
            missing_skills,
            key=lambda x: (
                0 if x["importance"] == "critical" else (1 if x["importance"] == "important" else 2)
            ),
        )

        learning_resources: List[Dict[str, Any]] = []
        for item in ranked[:4]:
            skill = item["skill"]
            learning_resources.append(
                {
                    "topic": skill,
                    "resource_name": f"Official {skill} Documentation & Interactive Tutorial",
                    "resource_type": "Documentation",
                    "url": f"https://www.google.com/search?q={skill}+official+documentation",
                }
            )
            learning_resources.append(
                {
                    "topic": skill,
                    "resource_name": f"Full Stack Masterclass: Building with {skill}",
                    "resource_type": "Course",
                    "url": f"https://www.coursera.org/search?query={skill}",
                }
            )

        # Project ideas that bridge gaps
        top_missing_names = [m["skill"] for m in ranked[:3]] or ["Docker", "PostgreSQL", "Next.js"]
        project_ideas = [
            {
                "title": f"Production-Ready Microservice with {top_missing_names[0]}",
                "description": f"Architect a cloud-native REST service utilizing {top_missing_names[0]} with comprehensive unit testing and CI/CD automation.",
                "technologies": top_missing_names,
                "key_features": [
                    "Secure JWT authentication and role-based access control",
                    "Automated database migrations with transaction rollbacks",
                    "Containerized multi-stage Docker deployment",
                ],
            },
            {
                "title": "Real-Time Collaborative Dashboard",
                "description": "Build an interactive, event-driven web application featuring live state synchronization and high-performance querying.",
                "technologies": top_missing_names[:2] + ["TypeScript", "Redis"],
                "key_features": [
                    "WebSocket / SSE pub-sub messaging architecture",
                    "Optimistic UI updates and offline resilience",
                    "Comprehensive end-to-end integration test suite",
                ],
            },
        ]

        resume_improvements = [
            "Quantify project impact with measurable metrics (e.g. 'Reduced latency by 35% through query optimization').",
            "Add direct links to GitHub repositories and live deployments for all featured applications.",
            f"Highlight specific practical experience with {', '.join(top_missing_names[:2])} prominently in the technical skills section.",
        ]

        interview_topics = [
            f"Core architecture and common pitfalls when working with {top_missing_names[0] if top_missing_names else 'modern frameworks'}.",
            "System design principles: Scalability, caching strategies, and database indexing.",
            "Handling distributed transactions and maintaining data consistency.",
        ]

        return {
            "missing_skills_ranked": ranked,
            "learning_resources": learning_resources,
            "project_ideas": project_ideas,
            "resume_improvements": resume_improvements,
            "interview_topics": interview_topics,
        }

    def _format_match_response(self, match_obj: Match) -> MatchResponse:
        component_scores_model = None
        if match_obj.component_scores:
            component_scores_model = ComponentScores(**match_obj.component_scores)

        improvement_plan_model = None
        if match_obj.improvement_plan:
            improvement_plan_model = ImprovementPlan(**match_obj.improvement_plan)

        return MatchResponse(
            id=match_obj.id,
            user_id=match_obj.user_id,
            resume_id=match_obj.resume_id,
            job_id=match_obj.job_id,
            overall_score=float(match_obj.overall_score)
            if match_obj.overall_score is not None
            else None,
            component_scores=component_scores_model,
            matched_skills=[MatchedSkillDetail(**m) for m in (match_obj.matched_skills or [])],
            missing_skills=[MissingSkillDetail(**m) for m in (match_obj.missing_skills or [])],
            partial_skills=[PartialSkillDetail(**p) for p in (match_obj.partial_skills or [])],
            evidence=match_obj.evidence or {},
            explanation=match_obj.explanation,
            strengths=match_obj.evidence.get("strengths", []) if match_obj.evidence else [],
            risks=match_obj.evidence.get("risks", []) if match_obj.evidence else [],
            improvement_plan=improvement_plan_model,
            model_name=match_obj.model_name,
            prompt_version=match_obj.prompt_version,
            status=match_obj.status,
            error_message=match_obj.error_message,
            created_at=match_obj.created_at,
            updated_at=match_obj.updated_at,
        )

    async def get_match(self, match_id: uuid.UUID, user_id: uuid.UUID) -> MatchResponse:
        match_obj = await self.match_repo.get_by_id_and_user(match_id, user_id)
        if not match_obj:
            raise NotFoundError("Match", match_id)
        return self._format_match_response(match_obj)

    async def list_matches(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 20
    ) -> Tuple[List[MatchResponse], int]:
        items, total = await self.match_repo.list_by_user(user_id, skip=skip, limit=limit)
        return [self._format_match_response(m) for m in items], total

    async def delete_match(self, match_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        match_obj = await self.match_repo.get_by_id_and_user(match_id, user_id)
        if not match_obj:
            raise NotFoundError("Match", match_id)
        await self.match_repo.delete(match_obj)
        return True
