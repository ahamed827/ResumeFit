import math
import re
from typing import Any, Dict, List

import httpx
from app.core.config import settings
from app.core.logging import logger

# Canonical Skill Alias Map
SKILL_ALIASES: Dict[str, str] = {
    "js": "javascript",
    "javascript": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "py": "python",
    "python": "python",
    "node": "node.js",
    "nodejs": "node.js",
    "node.js": "node.js",
    "react": "react",
    "reactjs": "react",
    "react.js": "react",
    "vue": "vue.js",
    "vuejs": "vue.js",
    "vue.js": "vue.js",
    "next": "next.js",
    "nextjs": "next.js",
    "next.js": "next.js",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "docker": "docker",
    "containerization": "docker",
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "pg": "postgresql",
    "mysql": "mysql",
    "mongo": "mongodb",
    "mongodb": "mongodb",
    "redis": "redis",
    "aws": "amazon web services",
    "amazon web services": "amazon web services",
    "gcp": "google cloud platform",
    "google cloud": "google cloud platform",
    "azure": "microsoft azure",
    "ci/cd": "ci/cd",
    "cicd": "ci/cd",
    "git": "git",
    "github": "git",
    "gitlab": "git",
    "rest": "restful apis",
    "restful": "restful apis",
    "rest api": "restful apis",
    "graphql": "graphql",
    "fastapi": "fastapi",
    "flask": "flask",
    "django": "django",
    "spring": "spring boot",
    "springboot": "spring boot",
    "spring boot": "spring boot",
    "java": "java",
    "c#": "c#",
    "csharp": "c#",
    ".net": ".net",
    "dotnet": ".net",
    "c++": "c++",
    "cpp": "c++",
    "golang": "go",
    "go": "go",
    "rust": "rust",
    "html": "html5",
    "html5": "html5",
    "css": "css3",
    "css3": "css3",
    "tailwind": "tailwindcss",
    "tailwindcss": "tailwindcss",
    "ml": "machine learning",
    "machine learning": "machine learning",
    "dl": "deep learning",
    "deep learning": "deep learning",
    "nlp": "natural language processing",
    "cv": "computer vision",
    "ai": "artificial intelligence",
    "llm": "large language models",
    "tensorflow": "tensorflow",
    "tf": "tensorflow",
    "pytorch": "pytorch",
    "scikit-learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "pandas": "pandas",
    "numpy": "numpy",
    "sql": "sql",
    "nosql": "nosql",
    "linux": "linux",
    "bash": "bash",
    "shell": "shell scripting",
    "terraform": "terraform",
    "ansible": "ansible",
}


def normalize_skill(skill: str) -> str:
    """Normalize skill name using canonical alias mapping."""
    clean = re.sub(r"[^\w\s\.\#\+\-]", "", skill).strip().lower()
    return SKILL_ALIASES.get(clean, clean)


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two numeric vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    magnitude1 = math.sqrt(sum(a * a for a in v1))
    magnitude2 = math.sqrt(sum(b * b for b in v2))
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)


def generate_local_semantic_vector(text: str, dim: int = 64) -> List[float]:
    """
    Deterministic character n-gram hashing vector for offline/local semantic similarity.
    Ensures identical strings or highly related substrings produce measurable similarity.
    """
    clean = text.lower().strip()
    vector = [0.0] * dim
    if not clean:
        return vector

    # Character trigrams
    trigrams = [clean[i : i + 3] for i in range(max(1, len(clean) - 2))]
    for tg in trigrams:
        h = hash(tg) % dim
        vector[h] += 1.0

    # Normalize vector to unit length
    magnitude = math.sqrt(sum(x * x for x in vector))
    if magnitude > 0:
        vector = [x / magnitude for x in vector]
    return vector


class EmbeddingService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.EMBEDDING_MODEL

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector using OpenAI API if configured, else local vector."""
        if self.provider == "openai" and self.api_key:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        f"{settings.OPENAI_BASE_URL}/embeddings",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={"input": text, "model": self.model},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        return data["data"][0]["embedding"]
                    else:
                        logger.warning(
                            f"OpenAI embedding API returned {resp.status_code}, falling back to local vector."
                        )
            except Exception as e:
                logger.warning(
                    f"Failed to fetch OpenAI embedding: {e}, falling back to local vector."
                )

        # Local deterministic semantic vector
        return generate_local_semantic_vector(text)

    async def match_skills(self, resume_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
        """
        Calculates direct matches, semantic matches, near matches, and missing skills.
        """
        normalized_resume = {s: normalize_skill(s) for s in resume_skills}
        reverse_resume = {}
        for original, norm in normalized_resume.items():
            reverse_resume.setdefault(norm, []).append(original)

        matched: List[Dict[str, Any]] = []
        partial: List[Dict[str, Any]] = []
        missing: List[str] = []

        for req_skill in job_skills:
            norm_req = normalize_skill(req_skill)

            # Direct or Alias Match
            if norm_req in reverse_resume:
                matched.append(
                    {
                        "skill": req_skill,
                        "matched_with": reverse_resume[norm_req][0],
                        "match_type": "direct_or_alias",
                        "similarity": 1.0,
                    }
                )
                continue

            # Substring match (e.g. "React" inside "React.js" or "Postgres" in "PostgreSQL")
            substring_found = False
            for original, norm in normalized_resume.items():
                if norm_req in norm or norm in norm_req:
                    matched.append(
                        {
                            "skill": req_skill,
                            "matched_with": original,
                            "match_type": "substring_match",
                            "similarity": 0.90,
                        }
                    )
                    substring_found = True
                    break

            if substring_found:
                continue

            # Semantic embedding vector match
            req_vec = await self.get_embedding(norm_req)
            best_sim = 0.0
            best_match = None

            for original, norm in normalized_resume.items():
                cand_vec = await self.get_embedding(norm)
                sim = cosine_similarity(req_vec, cand_vec)
                if sim > best_sim:
                    best_sim = sim
                    best_match = original

            if best_sim >= 0.85 and best_match:
                matched.append(
                    {
                        "skill": req_skill,
                        "matched_with": best_match,
                        "match_type": "semantic",
                        "similarity": round(best_sim, 2),
                    }
                )
            elif best_sim >= 0.65 and best_match:
                partial.append(
                    {
                        "skill": req_skill,
                        "related_resume_skill": best_match,
                        "similarity": round(best_sim, 2),
                        "explanation": f"Candidate has transferable familiarity via {best_match}.",
                    }
                )
            else:
                missing.append(req_skill)

        return {"matched": matched, "partial": partial, "missing": missing}


embedding_service = EmbeddingService()
