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
        # Strip user prompt wrapper if present
        clean_text = text
        if "Resume Text:" in clean_text:
            clean_text = clean_text.split("Resume Text:", 1)[1]
        clean_text = clean_text.strip(" \"'\n\r")

        lines = [
            l.strip()
            for l in clean_text.split("\n")
            if l.strip() and not l.strip().startswith('"""')
        ]

        # Full Name: Find first realistic name in top lines
        candidate_name = "Candidate"
        for line in lines[:8]:
            lower_line = line.lower()
            if any(
                h in lower_line
                for h in ["resume", "curriculum", "vitae", "profile", "summary", "contact"]
            ):
                continue
            if (
                len(line) <= 50
                and "@" not in line
                and not any(c.isdigit() for c in line)
                and not any(line.startswith(c) for c in ["+", "-", "*", "•"])
            ):
                candidate_name = line
                break

        # Email & Phone
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", clean_text)
        phone_match = re.search(
            r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}", clean_text
        )

        # LinkedIn & GitHub (supports with or without https:// protocol prefix)
        linkedin_match = re.search(
            r"(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_\-]+)",
            clean_text,
            re.IGNORECASE,
        )
        github_match = re.search(
            r"(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_\-]+)",
            clean_text,
            re.IGNORECASE,
        )

        # Professional Summary
        summary = None
        summary_match = re.search(
            r"(?:PROFESSIONAL\s+SUMMARY|SUMMARY|PROFILE|OBJECTIVE)\s*([\s\S]*?)(?:EDUCATION|TECHNICAL\s+SKILLS|SKILLS|EXPERIENCE|WORK\s+EXPERIENCE|PROJECTS|$)",
            clean_text,
            re.IGNORECASE,
        )
        if summary_match and summary_match.group(1).strip():
            summary = " ".join(summary_match.group(1).strip().split())

        # Education extraction
        education = []
        edu_match = re.search(
            r"EDUCATION\s*([\s\S]*?)(?:TECHNICAL\s+SKILLS|SKILLS|PROJECTS|EXPERIENCE|WORK\s+EXPERIENCE|CERTIFICATIONS|$)",
            clean_text,
            re.IGNORECASE,
        )
        edu_text = edu_match.group(1).strip() if edu_match else clean_text
        degree_regex = re.compile(
            r"\b(Bachelor(?:'?s)?(?:\s+of\s+[A-Za-z\s&]+)?|B\.?Tech|B\.?E\.?|B\.?S\.?(?:\b|\.)|B\.?Sc|BCA|BBA|"
            r"Master(?:'?s)?(?:\s+of\s+[A-Za-z\s&]+)?|M\.?Tech|M\.?E\.?|M\.?S\.?(?:\b|\.)|M\.?Sc|MCA|MBA|"
            r"Ph\.?D\.?|Doctorate|Diploma|Intermediate|Higher\s+Secondary|High\s+School)\b",
            re.IGNORECASE,
        )

        curr_edu = None
        for line in [l.strip() for l in edu_text.split("\n") if l.strip()]:
            deg_m = degree_regex.search(line)
            if deg_m:
                if curr_edu:
                    education.append(curr_edu)
                field = "Computer Science"
                if re.search(r"\bin\s+([A-Za-z\s&]+)", line, re.IGNORECASE):
                    field = (
                        re.search(r"\bin\s+([A-Za-z\s&]+)", line, re.IGNORECASE).group(1).strip()
                    )
                elif "(" in line and ")" in line:
                    field = line.split("(")[1].split(")")[0].strip()

                clean_degree = line
                clean_degree = re.sub(
                    r"\s*(?:August|July|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{4}).*$",
                    "",
                    clean_degree,
                    flags=re.IGNORECASE,
                ).strip()
                if not clean_degree:
                    clean_degree = line

                curr_edu = {
                    "degree": clean_degree,
                    "field_of_study": field,
                    "institution": "University / Institute",
                    "graduation_year": None,
                    "gpa": None,
                }
            elif curr_edu:
                if any(
                    term in line.lower()
                    for term in [
                        "college",
                        "university",
                        "institute",
                        "school",
                        "academy",
                        "campus",
                    ]
                ):
                    curr_edu["institution"] = re.sub(
                        r"\s*(?:CGPA|GPA|Score).*$", "", line, flags=re.IGNORECASE
                    ).strip()
                gpa_m = re.search(
                    r"(?:CGPA|GPA|Score|Marks|Percentage)?[:\s]*(\d{1,2}(?:\.\d{1,2})?\s*(?:/\s*10|%)?)",
                    line,
                    re.IGNORECASE,
                )
                if gpa_m and any(k in line.lower() for k in ["cgpa", "score", "gpa", "marks", "%"]):
                    curr_edu["gpa"] = gpa_m.group(0).strip()
                years = re.findall(r"\b(20[0-2]\d)\b", line)
                if years:
                    curr_edu["graduation_year"] = years[-1]
        if curr_edu:
            education.append(curr_edu)

        # Skills extraction: parse TECHNICAL SKILLS section + keyword fallback
        skills_set = set()
        skills_match = re.search(
            r"(?:TECHNICAL\s+SKILLS|SKILLS)\s*([\s\S]*?)(?:PROJECTS|EXPERIENCE|WORK\s+EXPERIENCE|EDUCATION|CERTIFICATIONS|$)",
            clean_text,
            re.IGNORECASE,
        )
        if skills_match:
            for line in skills_match.group(1).split("\n"):
                line = line.strip()
                if ":" in line:
                    after_colon = line.split(":", 1)[1]
                    for s in re.split(r"[,;•|/]", after_colon):
                        item = s.strip().rstrip(".")
                        if item and len(item) < 35:
                            skills_set.add(item)

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
            "GitHub",
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
            "Deep Learning",
            "Generative AI",
            "PyTorch",
            "TensorFlow",
            "Pandas",
            "NumPy",
            "CI/CD",
            "REST APIs",
            "Prisma ORM",
        ]
        for s in known_skills:
            if re.search(r"\b" + re.escape(s) + r"\b", clean_text, re.IGNORECASE):
                skills_set.add(s)

        # Projects extraction
        projects = []
        proj_match = re.search(
            r"PROJECTS\s*([\s\S]*?)(?:CERTIFICATIONS|WORK\s+EXPERIENCE|EXPERIENCE|PUBLICATIONS|$)",
            clean_text,
            re.IGNORECASE,
        )
        if proj_match:
            curr_proj = None
            for line in proj_match.group(1).split("\n"):
                l = line.strip()
                if not l or l in ["\u2014", "GitHub", "GitLab"] or re.match(r"^20\d\d$", l):
                    continue
                is_bullet = l.startswith("\u2022") or l.startswith("-") or l.startswith("*")
                is_tech = l.lower().startswith("tech stack:") or l.lower().startswith(
                    "technologies:"
                )
                if not is_bullet and not is_tech and len(l) < 80 and not l.endswith("."):
                    if curr_proj and curr_proj["name"]:
                        projects.append(curr_proj)
                    clean_title = re.sub(
                        r"\s*[—–-]?\s*(?:GitHub|Gitlab)?\s*(?:20\d\d)?\s*$",
                        "",
                        l,
                        flags=re.IGNORECASE,
                    ).strip()
                    curr_proj = {
                        "name": clean_title,
                        "description": "",
                        "technologies_used": [],
                        "url": None,
                        "achievements": [],
                    }
                elif curr_proj:
                    if is_tech:
                        techs = re.sub(
                            r"^(?:Tech Stack|Technologies)[:\s]*", "", l, flags=re.IGNORECASE
                        )
                        curr_proj["technologies_used"] = [
                            t.strip().rstrip(".") for t in re.split(r"[,;•|]", techs) if t.strip()
                        ]
                    elif is_bullet:
                        bullet_clean = re.sub(r"^[\u2022\-*]\s*", "", l).strip()
                        if not curr_proj["description"]:
                            curr_proj["description"] = bullet_clean
                        curr_proj["achievements"].append(bullet_clean)
                    else:
                        if curr_proj["achievements"]:
                            curr_proj["achievements"][-1] += " " + l
                        elif curr_proj["description"]:
                            curr_proj["description"] += " " + l
            if curr_proj and curr_proj["name"]:
                projects.append(curr_proj)

        # Certifications extraction
        certifications = []
        cert_match = re.search(
            r"CERTIFICATIONS?\s*([\s\S]*?)(?:PUBLICATIONS|ACHIEVEMENTS|LANGUAGES|$)",
            clean_text,
            re.IGNORECASE,
        )
        if cert_match:
            for line in cert_match.group(1).split("\n"):
                l = line.strip()
                if l and (l.startswith("\u2022") or l.startswith("-") or l.startswith("*")):
                    clean_cert = re.sub(r"^[\u2022\-*]\s*", "", l).strip()
                    parts = re.split(r"\s*[—–-]\s*", clean_cert, 1)
                    cert_name = parts[0].strip()
                    issuer = parts[1].replace("Active", "").strip() if len(parts) > 1 else None
                    certifications.append(
                        {
                            "name": cert_name,
                            "issuing_organization": issuer,
                            "issue_date": None,
                            "credential_url": None,
                        }
                    )

        return {
            "full_name": candidate_name,
            "email": email_match.group(0).strip() if email_match else None,
            "phone": phone_match.group(0).strip() if phone_match else None,
            "location": None,
            "linkedin": (
                f"https://linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else None
            ),
            "github": (f"https://github.com/{github_match.group(1)}" if github_match else None),
            "portfolio": None,
            "professional_summary": summary,
            "skills": sorted(list(skills_set)),
            "education": education,
            "work_experience": [],
            "internships": [],
            "projects": projects,
            "certifications": certifications,
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
