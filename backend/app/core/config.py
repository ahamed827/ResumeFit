import json
from typing import List, Optional, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "ResumeFit"
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"

    # Security & Tokens
    SECRET_KEY: str = "change-me-super-secret-hex-token-min-32-chars-long-for-production!"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://resumefit_user:resumefit_secure_password@localhost:5432/resumefit_db"
    )
    DATABASE_SYNC_URL: str = (
        "postgresql://resumefit_user:resumefit_secure_password@localhost:5432/resumefit_db"
    )

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    ALLOWED_CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        if not self.ALLOWED_CORS_ORIGINS:
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_CORS_ORIGINS.split(",") if origin.strip()]

    # AI & LLM Service
    LLM_PROVIDER: str = "openai"  # "openai", "azure", or "local_heuristic"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 3000
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Matching Weights (must sum to 1.0)
    WEIGHT_REQUIRED_SKILLS: float = 0.40
    WEIGHT_EXPERIENCE: float = 0.20
    WEIGHT_NICE_TO_HAVE_SKILLS: float = 0.15
    WEIGHT_PROJECTS: float = 0.10
    WEIGHT_EDUCATION: float = 0.10
    WEIGHT_SENIORITY: float = 0.05

    # Storage
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    LOCAL_STORAGE_DIR: str = "./uploads"
    MAX_FILE_SIZE_BYTES: int = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS: Union[List[str], str] = [".pdf", ".docx", ".txt"]
    ALLOWED_MIME_TYPES: Union[List[str], str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "text/plain",
    ]

    @field_validator("ALLOWED_EXTENSIONS", "ALLOWED_MIME_TYPES", mode="after")
    @classmethod
    def parse_comma_or_json_list(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    # S3
    S3_BUCKET_NAME: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_ENDPOINT_URL: Optional[str] = None

    # Email
    EMAIL_PROVIDER: str = "console"  # "console" or "smtp"
    EMAILS_FROM_EMAIL: str = "no-reply@resumefit.io"
    EMAILS_FROM_NAME: str = "ResumeFit Team"
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True

    # Rate Limiting
    RATE_LIMIT_LOGIN: str = "5/15minute"
    RATE_LIMIT_REGISTER: str = "5/hour"
    RATE_LIMIT_UPLOAD: str = "10/hour"
    RATE_LIMIT_MATCH: str = "20/hour"


settings = Settings()
