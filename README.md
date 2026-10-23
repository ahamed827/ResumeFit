# ResumeFit — AI-Powered Resume-to-Job Matcher

[![CI/CD Pipeline](https://github.com/your-username/resume-fit/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/resume-fit/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ResumeFit is a production-quality, portfolio-grade web application engineered for computer science freshers and software engineers. It automates resume evaluation against real job specifications using **transparent, deterministic 6-factor scoring**, **alias-aware semantic skill matching**, **verifiable evidence extraction**, and **personalized career roadmaps**.

---

## 1. Key Features

- **Document Ingestion**: Upload PDF or DOCX resumes (up to 5MB) with automatic scanned-document detection, text extraction, and strict Pydantic v2 structuring.
- **Job Description Analysis**: Paste raw postings or upload files to partition must-have vs nice-to-have requirements, experience thresholds, and responsibilities.
- **Explainable 0–100 Scoring**: Weighted across Required Skills (40%), Experience (20%), Nice-to-haves (15%), Projects (10%), Education (10%), and Seniority (5%).
- **Verifiable Evidence Quotes**: Every matched technical competency is paired directly with verbatim evidence from your resume projects and work history.
- **Alias-Aware Skill Normalization**: Canonical dictionary resolves variations automatically (`JS` &rarr; `JavaScript`, `K8s` &rarr; `Kubernetes`, `Postgres` &rarr; `PostgreSQL`).
- **Personalized Improvement Plan**: Targeted gap analysis ranking missing skills by criticality, offering official learning resources, and detailing portfolio project ideas.
- **Tailored Professional Summary**: Synthesizes fact-backed 3–4 sentence executive summaries without hallucinating unverified experience.
- **Application Pipeline Tracker**: Kanban-style status board (`Saved`, `Applied`, `Screening`, `Interview`, `Technical Assessment`, `Offer`, `Rejected`, `Withdrawn`).
- **Role-Based Access Control**: Strict candidate, recruiter, and admin authorization boundaries.
- **Admin Observability Dashboard**: Platform telemetry, AI success rate, token consumption, latency, and user account management.

---

## 2. Architecture Overview

ResumeFit strictly adheres to a clean layered architecture:

```
resume-fit/
├── frontend/                     # Next.js 14 App Router, TypeScript, Tailwind CSS
│   ├── src/
│   │   ├── app/                  # App router pages (dashboard, resumes, jobs, matches, apps, admin)
│   │   ├── components/           # UI components, layout shell, navbar
│   │   ├── features/auth/        # Auth context, state, token interceptors
│   │   ├── lib/                  # Axios client, auto-refresh queue, utils
│   │   └── types/                # Domain TypeScript interfaces
├── backend/                      # Python 3.11+ FastAPI Clean Layered Service
│   ├── app/
│   │   ├── api/v1/endpoints/     # REST routers: auth, resumes, jobs, matches, apps, summaries, admin
│   │   ├── core/                 # Config (Pydantic settings), security, logging, errors, rate limiter
│   │   ├── db/                   # Async SQLAlchemy engine, session maker, base models
│   │   ├── models/               # SQLAlchemy 2.0 ORM entities
│   │   ├── schemas/              # Pydantic v2 request/response & LLM output schemas
│   │   ├── services/             # Business logic (matching engine, auth, resumes, jobs, summaries)
│   │   ├── repositories/         # Database access layer
│   │   ├── integrations/         # Storage adapter, document parser, LLM client, embeddings, email
│   │   ├── workers/              # Asynchronous background tasks worker
│   │   └── main.py               # FastAPI entrypoint, lifespan, CORS, middleware
│   ├── tests/                    # 21 comprehensive pytest integration and unit tests
│   └── alembic/                  # Database migration scripts
├── prompts/                      # Strict JSON-schema prompts for LLM extraction tasks
├── evaluation/                   # 10 resumes, 10 jobs, 30 pairs benchmark suite & scripts
├── docker-compose.yml            # Multi-service local production orchestrator
├── .env.example                  # Environment configuration template
├── ARCHITECTURE.md               # Mermaid system and pipeline diagrams
├── API.md                        # Complete REST API reference
├── TESTING.md                    # Test execution instructions and coverage
├── DEPLOYMENT.md                 # Cloud deployment instructions (Railway, Render, AWS)
└── EVALUATION.md                 # Benchmark results across 30 evaluation pairs
```

---

## 3. Demo Credentials

The platform automatically seeds an administrator account on first boot:

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@resumefit.io` | `AdminPass123!` |
| **Candidate** | Self-register via `/register` or demo credentials in UI | Minimum 8 characters |

---

## 4. Quick Start (Local Development)

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- PostgreSQL and Redis (or run via Docker Compose)

### Option 1: Run with Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/resume-fit.git
cd resume-fit

# Copy environment variables
cp .env.example .env

# Start all services (PostgreSQL, Redis, Backend, Worker, Frontend)
docker compose up -d --build

# Run migrations
docker compose exec backend alembic upgrade head

# Access the applications:
# Frontend: http://localhost:3000
# Backend API & Swagger: http://localhost:8000/docs
```

### Option 2: Run Locally (Host Machine)

#### 1. Backend Setup
```bash
# Create and activate Python virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux / macOS

# Install backend dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Start backend API server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup
```bash
cd frontend

# Install npm dependencies
npm install

# Start Next.js development server
npm run dev
```

Visit `http://localhost:3000` in your browser.

---

## 5. Running Tests & Benchmarks

```bash
# 1. Run all 21 automated backend tests
pytest backend/tests -v

# 2. Check frontend TypeScript types
cd frontend
npm run typecheck

# 3. Execute 30-pair evaluation benchmark
python evaluation/run_evaluation.py
```

---

## 6. Multi-Stage AI Pipeline

1. **Stage 1: Document Extraction** &rarr; PyMuPDF/python-docx parses raw text; rejects image-only or flattened scans.
2. **Stage 2: Resume Structuring** &rarr; Validates technical proficiencies, education, work history, and projects against `StructuredResumeProfile`.
3. **Stage 3: Job Structuring** &rarr; Separates must-have requirements from nice-to-haves and extracts seniority.
4. **Stage 4: Semantic Skill Matching** &rarr; Generates vector embeddings with alias-aware mapping (`JS` &rarr; `JavaScript`).
5. **Stage 5: Evidence-Based Evaluation** &rarr; Maps verbatim resume quotes to requirements.
6. **Stage 6: Personalized Roadmap** &rarr; Generates ranked missing skills, practical project ideas, and learning links.

---

## 7. Security & Privacy Highlights

- **Bcrypt Password Hashing**: Passwords hashed with high-cost salt factors.
- **Short-Lived JWT Tokens**: 15-minute access tokens + 7-day refresh tokens with rotation and revocation tracking.
- **Rate Limiting**: Sliding window rate limits on login (5/15m), register (5/h), uploads (10/h), and matching (20/h).
- **Data Minimization & Masking**: Candidate resume raw text is masked from recruiters and administrators in the UI.
- **No Hallucinated Claims**: LLM outputs are validated against Pydantic schemas with automatic retries on schema invalidity.

---

## 8. Known Limitations & Next Steps

- **Scanned PDF OCR**: Currently, scanned image-only PDFs are rejected with a clear user prompt to provide selectable text. Future enhancement: integrate Tesseract OCR.
- **Vector Database**: Currently supports pgvector and local cosine vector projections. Future enhancement: direct Pinecone/Weaviate sync for large enterprise resume libraries.
- **Real-Time WebSockets**: Currently uses responsive polling for background tasks. Future enhancement: direct WebSocket push notifications for worker job completions.

---

## 9. License

This project is licensed under the MIT License.
