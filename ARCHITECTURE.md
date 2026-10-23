# ResumeFit System Architecture

ResumeFit is an AI-powered resume-to-job matcher and application tracking system engineered with a clean layered architecture, deterministic explainability, and multi-stage LLM evaluation.

---

## 1. High-Level Architecture Overview

```mermaid
flowchart TD
    subgraph Client["Presentation Layer (Client)"]
        UI["Next.js 14 App Router (React, TypeScript, Tailwind CSS)"]
        State["TanStack React Query + React Hook Form + Zod"]
        AuthContext["Auth Context (JWT + Refresh Rotation)"]
    end

    subgraph API_GW["API & Security Layer"]
        FastAPI["FastAPI 0.111+ Backend"]
        RateLimit["Rate Limiter (Sliding Window Redis/Memory)"]
        SecMiddleware["Structured Logging & Global Exception Handlers"]
    end

    subgraph Business["Service Layer (Domain Logic)"]
        AuthSvc["AuthService (bcrypt, JWT rotation)"]
        ResumeSvc["ResumeService (Document Parser, Pydantic Schema)"]
        JobSvc["JobService (Requirement Structuring)"]
        MatchEngine["MatchingEngine (6 Weighted Factors, Deterministic)"]
        SummarySvc["SummaryService (Evidence-Based Synthesis)"]
        AppSvc["ApplicationService (Kanban & Pipeline Tracker)"]
    end

    subgraph Integrations["Integration Layer"]
        Storage["StorageService (Local Filesystem / S3 Adapter)"]
        DocExtract["DocumentParser (PyMuPDF, python-docx, TXT)"]
        LLM["LLMService (OpenAI / Local Heuristic Fallback)"]
        Embed["EmbeddingService (Cosine Similarity, Alias Map)"]
        Email["EmailService (Console Preview / SMTP TLS)"]
    end

    subgraph Data["Persistence & Caching Layer"]
        PG[(PostgreSQL 16 Relational DB)]
        Redis[(Redis 7 In-Memory Cache & Tasks)]
        Filesystem[(Secure File Store /uploads)]
    end

    UI -->|HTTP / REST (JSON)| FastAPI
    FastAPI --> RateLimit
    RateLimit --> SecMiddleware
    SecMiddleware --> Business

    ResumeSvc --> Storage
    ResumeSvc --> DocExtract
    ResumeSvc --> LLM

    JobSvc --> DocExtract
    JobSvc --> LLM

    MatchEngine --> Embed
    MatchEngine --> LLM

    SummarySvc --> LLM
    AuthSvc --> Email

    Business --> PG
    Business --> Redis
    Storage --> Filesystem
```

---

## 2. Multi-Stage AI Matching Pipeline

ResumeFit rejects single-prompt raw matching. Instead, it processes inputs through an explainable, 6-stage pipeline:

```mermaid
sequenceDiagram
    autonumber
    actor Candidate as User / Candidate
    participant API as FastAPI Backend
    participant DocParser as Document Parser
    participant LLM as LLM Service
    participant Embed as Embedding Service
    participant Engine as Matching Engine
    participant DB as PostgreSQL DB

    Candidate->>API: Upload Resume (PDF / DOCX)
    API->>DocParser: Extract raw text & detect scanned PDF
    DocParser-->>API: Raw cleaned text
    API->>LLM: Stage 2: Structure resume into Pydantic schema
    LLM-->>API: StructuredResumeProfile (JSON)
    API->>DB: Store structured profile

    Candidate->>API: Submit Job Description
    API->>LLM: Stage 3: Extract structured requirements
    LLM-->>API: StructuredJobRequirements (Must-have vs Nice-to-have)
    API->>DB: Store structured job

    Candidate->>API: Request Match Evaluation
    API->>Engine: Run 6-factor deterministic pipeline
    Engine->>Embed: Stage 4: Alias-aware matching (JS->JavaScript, K8s->Kubernetes)
    Embed-->>Engine: Matched, partial, and missing skills
    Engine->>Engine: Stage 5: Evidence quote mapping from resume projects
    Engine->>Engine: Compute weighted score (0 - 100)
    Engine->>Engine: Stage 6: Generate personalized improvement plan
    Engine->>DB: Store match report & token telemetry
    DB-->>Candidate: Return 0-100 score, evidence quotes, and roadmap
```

---

## 3. Database Entity Relationship Diagram

```mermaid
erDiagram
    users ||--o{ refresh_tokens : owns
    users ||--o{ resumes : uploads
    users ||--o{ jobs : creates
    users ||--o{ matches : runs
    users ||--o{ applications : tracks
    users ||--o{ resume_summaries : generates
    users ||--o{ ai_usage_logs : generates

    resumes ||--o{ matches : evaluated_in
    resumes ||--o{ applications : attached_to
    resumes ||--o{ resume_summaries : referenced_by

    jobs ||--o{ matches : target_for
    jobs ||--o{ applications : tracks_role
    jobs ||--o{ resume_summaries : tailored_for

    users {
        uuid id PK
        string email UK
        string password_hash
        string full_name
        enum role "candidate | recruiter | admin"
        boolean is_active
        boolean email_verified
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }

    refresh_tokens {
        uuid id PK
        uuid user_id FK
        string token_hash UK
        timestamp expires_at
        timestamp revoked_at
        timestamp created_at
    }

    resumes {
        uuid id PK
        uuid user_id FK
        string original_filename
        string file_url
        int file_size_bytes
        string mime_type
        enum extraction_status
        text raw_text
        jsonb structured_profile
        text parsing_error
        timestamp created_at
        timestamp deleted_at
    }

    jobs {
        uuid id PK
        uuid user_id FK
        string title
        string company_name
        enum source_type
        text raw_description
        jsonb structured_requirements
        enum analysis_status
        timestamp created_at
        timestamp deleted_at
    }

    matches {
        uuid id PK
        uuid user_id FK
        uuid resume_id FK
        uuid job_id FK
        numeric overall_score
        jsonb component_scores
        jsonb matched_skills
        jsonb missing_skills
        jsonb partial_skills
        jsonb evidence
        text explanation
        jsonb improvement_plan
        string model_name
        timestamp created_at
    }

    applications {
        uuid id PK
        uuid user_id FK
        uuid job_id FK
        uuid resume_id FK
        enum status "saved | applied | screening | interview | offer | rejected"
        text notes
        timestamp applied_at
        timestamp deadline
        timestamp created_at
    }

    ai_usage_logs {
        uuid id PK
        uuid user_id FK
        enum task_type
        string model_name
        int prompt_tokens
        int completion_tokens
        int total_tokens
        numeric estimated_cost_usd
        int latency_ms
        enum status
        timestamp created_at
    }
```

---

## 4. Deterministic Scoring Model

The final score is computed through an explainable, 6-factor weighted algorithm:

$$\text{Overall Score} = \sum_{i=1}^{6} (w_i \times S_i)$$

Where the default component weights are:
1. **Required Skills ($S_1$)**: 40% weight ($w_1 = 0.40$)
2. **Experience Relevance ($S_2$)**: 20% weight ($w_2 = 0.20$)
3. **Nice-to-Have Skills ($S_3$)**: 15% weight ($w_3 = 0.15$)
4. **Projects & Practical Evidence ($S_4$)**: 10% weight ($w_4 = 0.10$)
5. **Education & Degree Fit ($S_5$)**: 10% weight ($w_5 = 0.10$)
6. **Seniority Alignment ($S_6$)**: 5% weight ($w_6 = 0.05$)

All component scores are normalized from $0.0$ to $100.0$. If a job posting does not require specific years of experience or degree credentials, the candidate is **not penalized** and receives standard baseline scores for those components.
