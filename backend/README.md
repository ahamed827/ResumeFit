# ResumeFit Backend Service

FastAPI-powered REST API for resume parsing, semantic matching, and application tracking.

## Architecture & Layers
- `app/api/v1/endpoints/`: Route handlers for auth, resumes, jobs, matches, applications, summaries, and admin.
- `app/core/`: Configuration, security (bcrypt & JWT), rate limiting, structured logging, custom exceptions.
- `app/db/`: Async SQLAlchemy 2.0 sessions and declarative Base model.
- `app/models/`: Relational schema definitions with PostgreSQL JSONB and UUID primary keys.
- `app/schemas/`: Strict Pydantic v2 validation models for all request, response, and LLM payloads.
- `app/services/`: Pure business logic (deterministic matching engine, auth, resumes, jobs).
- `app/repositories/`: Database interaction queries and transactions.
- `app/integrations/`: Storage adapters (local/S3), document parser (PyMuPDF/docx), LLM service, embeddings.
- `app/workers/`: Background task worker.

## Running Tests
```bash
pytest tests -v
```

## Running Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
