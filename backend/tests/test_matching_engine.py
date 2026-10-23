import pytest
from app.integrations.embedding_service import normalize_skill, embedding_service
from app.services.matching_engine import MatchingEngine


def test_skill_normalization_and_aliases():
    assert normalize_skill("JS") == "javascript"
    assert normalize_skill("TypeScript") == "typescript"
    assert normalize_skill("k8s") == "kubernetes"
    assert normalize_skill("Postgres") == "postgresql"
    assert normalize_skill("Node") == "node.js"
    assert normalize_skill("react.js") == "react"


@pytest.mark.asyncio
async def test_semantic_skill_matching():
    resume_skills = ["Python", "JavaScript", "Docker", "PostgreSQL", "FastAPI"]
    job_skills = ["JS", "Python", "Kubernetes", "Postgres", "Redis"]

    result = await embedding_service.match_skills(resume_skills, job_skills)

    matched_names = [m["skill"] for m in result["matched"]]
    assert "JS" in matched_names  # Matched with JavaScript
    assert "Python" in matched_names
    assert "Postgres" in matched_names  # Matched with PostgreSQL

    missing_names = result["missing"]
    assert "Redis" in missing_names


@pytest.mark.asyncio
async def test_deterministic_scoring_weights(db_session):
    engine = MatchingEngine(db_session)

    resume_profile = {
        "full_name": "Test Engineer",
        "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
        "education": [{
            "degree": "Bachelor of Science",
            "field_of_study": "Computer Science",
            "institution": "Tech University",
            "graduation_year": "2024"
        }],
        "work_experience": [{
            "title": "Software Engineer Intern",
            "organization": "Acme Corp",
            "technologies_used": ["Python", "FastAPI", "PostgreSQL"]
        }],
        "projects": [
            {
                "name": "E-Commerce Microservice",
                "technologies_used": ["Python", "Docker", "PostgreSQL"],
                "description": "Built resilient REST APIs."
            },
            {
                "name": "Task Scheduler",
                "technologies_used": ["Python", "FastAPI"],
                "description": "Implemented background queue."
            }
        ]
    }

    job_reqs = {
        "job_title": "Backend Developer",
        "seniority_level": "Entry / Mid Level",
        "must_have_skills": ["Python", "PostgreSQL", "FastAPI"],
        "nice_to_have_skills": ["Kubernetes", "AWS"],
        "education_requirements": ["Bachelor's degree in Computer Science"],
        "years_of_experience": 1.0
    }

    match_result = await engine._execute_matching_pipeline(
        resume_profile=resume_profile,
        job_reqs=job_reqs,
        resume_raw="Full text with Python, FastAPI, Docker, and PostgreSQL projects.",
        job_raw="Looking for a Backend Developer with Python, FastAPI, and PostgreSQL."
    )

    score = match_result["overall_score"]
    assert 0 <= score <= 100
    # Must-have skills are 100% satisfied (Python, Postgres, FastAPI)
    assert match_result["component_scores"]["required_skills"] == 100.0
    assert match_result["component_scores"]["education_fit"] == 100.0
    assert len(match_result["matched_skills"]) >= 3
    assert len(match_result["missing_skills"]) >= 1  # Kubernetes / AWS missing
    assert match_result["explanation"] is not None
    assert len(match_result["explanation"]) > 30
