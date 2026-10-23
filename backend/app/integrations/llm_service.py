import json
import re
import time
from typing import Any, Dict, Type, TypeVar

import httpx
from app.core.config import settings
from app.core.logging import logger
from app.schemas.job import StructuredJobRequirements
from app.schemas.resume import (
    StructuredResumeProfile,
)
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)
Tuple_Result = Any


class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL.rstrip("/")
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS

    async def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Type[T],
        task_name: str = "generic",
        max_retries: int = 3,
    ) -> Tuple_Result:
        """
        Calls the LLM with structured output, validates against Pydantic schema,
        and retries up to max_retries with backoff on validation errors.
        """
        # If configured for local heuristic fallback or missing API key, use deterministic parsing
        if (
            self.provider == "local_heuristic"
            or not self.api_key
            or self.api_key.startswith("your-")
        ):
            return self._heuristic_fallback(system_prompt, user_prompt, schema, task_name)

        last_error = None
        for attempt in range(1, max_retries + 1):
            start_time = time.perf_counter()
            try:
                async with httpx.AsyncClient(timeout=45.0) as client:
                    resp = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                            ],
                            "temperature": self.temperature,
                            "max_tokens": self.max_tokens,
                            "response_format": {"type": "json_object"},
                        },
                    )

                latency_ms = int((time.perf_counter() - start_time) * 1000)

                if resp.status_code != 200:
                    error_msg = f"LLM API returned status {resp.status_code}: {resp.text}"
                    logger.warning(f"Attempt {attempt} failed: {error_msg}")
                    last_error = error_msg
                    time.sleep(attempt * 0.5)
                    continue

                res_json = resp.json()
                raw_content = res_json["choices"][0]["message"]["content"]
                usage = res_json.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

                # Cost estimation for gpt-4o-mini ($0.15 / 1M prompt, $0.60 / 1M completion)
                cost = (prompt_tokens * 0.00000015) + (completion_tokens * 0.00000060)

                # Parse JSON
                parsed_dict = json.loads(raw_content)
                validated_obj = schema.model_validate(parsed_dict)

                return (
                    validated_obj,
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    cost,
                    latency_ms,
                    self.model,
                )

            except (ValidationError, json.JSONDecodeError) as val_err:
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                logger.warning(f"LLM output validation error on attempt {attempt}: {val_err}")
                last_error = str(val_err)
                time.sleep(attempt * 0.5)

            except Exception as e:
                logger.error(f"Unexpected error calling LLM on attempt {attempt}: {e}")
                last_error = str(e)
                time.sleep(attempt * 0.5)

        # If LLM attempts failed or rate limited, gracefully fall back to local heuristic parser
        logger.warning(
            f"All {max_retries} LLM attempts failed ({last_error}). Falling back to local heuristic engine."
        )
        return self._heuristic_fallback(system_prompt, user_prompt, schema, task_name)

    def _heuristic_fallback(
        self, system_prompt: str, user_prompt: str, schema: Type[T], task_name: str
    ) -> Any:
        """
        Offline deterministic fallback parser to ensure the application works reliably
        even without third-party internet dependencies or during testing.
        """
        start = time.perf_counter()

        if schema == StructuredResumeProfile:
            data = self._heuristic_parse_resume(user_prompt)
            obj = schema.model_validate(data)
        elif schema == StructuredJobRequirements:
            data = self._heuristic_parse_job(user_prompt)
            obj = schema.model_validate(data)
        else:
            # Generic empty/sensible mock for other schemas
            data = {}
            obj = schema.model_validate(data)

        latency = int((time.perf_counter() - start) * 1000)
        return (obj, 100, 150, 250, 0.0, latency, "local-heuristic-v1")

    def _heuristic_parse_resume(self, text: str) -> Dict[str, Any]:
        """Heuristic rule-based extractor for resume text."""
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        phone_match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        linkedin_match = re.search(r"(https?://(?:www\.)?linkedin\.com/in/[\w-]+)", text)
        github_match = re.search(r"(https?://(?:www\.)?github\.com/[\w-]+)", text)

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        full_name = lines[0] if lines else "Candidate"
        if len(full_name) > 50 or "@" in full_name:
            full_name = "Candidate"

        # Known skills keyword lookup
        known_skills = [
            "Python",
            "JavaScript",
            "TypeScript",
            "React",
            "Node.js",
            "Docker",
            "Kubernetes",
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "Redis",
            "AWS",
            "Git",
            "FastAPI",
            "Django",
            "Flask",
            "Tailwind CSS",
            "Next.js",
            "GraphQL",
            "C++",
            "Java",
            "Linux",
            "SQL",
            "HTML5",
            "CSS3",
            "Machine Learning",
            "PyTorch",
            "TensorFlow",
            "Pandas",
            "NumPy",
            "CI/CD",
            "REST API",
        ]
        found_skills = []
        for s in known_skills:
            if re.search(r"\b" + re.escape(s) + r"\b", text, re.IGNORECASE):
                found_skills.append(s)

        # Detect education degrees
        education = []
        degree_patterns = [
            r"(Bachelor\s+of\s+[A-Za-z\s]+|B\.?S\.?|B\.?Tech|Master\s+of\s+[A-Za-z\s]+|M\.?S\.?|Ph\.?D\.?)",
            r"(Computer\s+Science|Information\s+Technology|Software\s+Engineering|Data\s+Science)",
        ]
        degree_match = re.search(degree_patterns[0], text, re.IGNORECASE)
        field_match = re.search(degree_patterns[1], text, re.IGNORECASE)
        year_match = re.search(r"\b(201\d|202\d)\b", text)

        if degree_match or field_match:
            education.append(
                {
                    "degree": degree_match.group(0).strip()
                    if degree_match
                    else "Bachelor of Science",
                    "field_of_study": field_match.group(0).strip()
                    if field_match
                    else "Computer Science",
                    "institution": "University / Institute",
                    "graduation_year": year_match.group(0) if year_match else None,
                    "gpa": None,
                }
            )

        # Detect projects / experience
        projects = []
        project_headers = re.findall(r"(?:Project|Portfolio):\s*([^\n]+)", text, re.IGNORECASE)
        for proj in project_headers[:3]:
            projects.append(
                {
                    "name": proj.strip(),
                    "description": "Implemented technical solution and software architecture.",
                    "technologies_used": found_skills[:3],
                    "url": None,
                    "achievements": ["Successfully delivered end-to-end functionality"],
                }
            )

        # Summary
        summary = None
        summary_match = re.search(
            r"(?:Summary|Profile|Objective):\s*([^\n]+(?:\n[^\n]+){1,3})", text, re.IGNORECASE
        )
        if summary_match:
            summary = summary_match.group(1).strip()
        else:
            summary = f"Aspiring software engineer skilled in {', '.join(found_skills[:4])} with hands-on project experience."

        return {
            "full_name": full_name,
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0) if phone_match else None,
            "location": None,
            "linkedin": linkedin_match.group(0) if linkedin_match else None,
            "github": github_match.group(0) if github_match else None,
            "portfolio": None,
            "professional_summary": summary,
            "skills": found_skills,
            "education": education,
            "work_experience": [],
            "internships": [],
            "projects": projects,
            "certifications": [],
            "achievements": [],
            "languages": ["English"],
        }

    def _heuristic_parse_job(self, text: str) -> Dict[str, Any]:
        """Heuristic rule-based extractor for job descriptions."""
        # Strip user template wrapper if present
        clean_text = text
        if "Job Description Text:" in clean_text:
            clean_text = clean_text.split("Job Description Text:", 1)[1]
        clean_text = clean_text.strip(" \"'\n\r")

        lines = [
            l.strip()
            for l in clean_text.split("\n")
            if l.strip() and not l.strip().startswith('"""')
        ]
        title = lines[0] if lines else "Software Engineer"
        if len(title) > 60 or "description" in title.lower():
            title = "Software Engineer"

        known_skills = [
            "Python",
            "JavaScript",
            "TypeScript",
            "React",
            "Node.js",
            "Docker",
            "Kubernetes",
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "Redis",
            "AWS",
            "Git",
            "FastAPI",
            "Django",
            "Tailwind CSS",
            "Next.js",
            "GraphQL",
            "Java",
            "C++",
            "Linux",
            "SQL",
            "Machine Learning",
            "CI/CD",
            "REST API",
        ]
        must_have = []
        nice_to_have = []

        for s in known_skills:
            if re.search(r"\b" + re.escape(s) + r"\b", text, re.IGNORECASE):
                if re.search(
                    r"(?:nice to have|preferred|bonus|plus).{0,50}\b" + re.escape(s) + r"\b",
                    text,
                    re.IGNORECASE,
                ):
                    nice_to_have.append(s)
                else:
                    must_have.append(s)

        # If no skills partitioned, place top 4 in must_have, rest in nice_to_have
        if not nice_to_have and len(must_have) > 4:
            nice_to_have = must_have[4:]
            must_have = must_have[:4]

        # Years of experience detection
        exp_match = re.search(r"(\d+)\+?\s*years?\s+(?:of\s+)?experience", text, re.IGNORECASE)
        years = float(exp_match.group(1)) if exp_match else None

        return {
            "job_title": title,
            "company_name": None,
            "seniority_level": "Entry / Mid Level" if not years or years <= 2 else "Senior Level",
            "employment_type": "Full-time",
            "location": "Remote / Hybrid",
            "must_have_skills": must_have,
            "nice_to_have_skills": nice_to_have,
            "responsibilities": [
                "Collaborate with cross-functional teams to design, build, and test features.",
                "Maintain clean code, tests, and technical documentation.",
            ],
            "education_requirements": ["Bachelor's degree in Computer Science or related field"],
            "experience_requirements": f"{years} years of professional experience"
            if years
            else None,
            "years_of_experience": years,
            "keywords": must_have + nice_to_have,
            "red_flags": [],
        }


# Type alias for return tuple
Tuple_Result = Any
llm_service = LLMService()
