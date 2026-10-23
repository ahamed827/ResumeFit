# ResumeFit REST API Specification (v1)

Base URL: `/api/v1`

All responses are formatted in JSON. Protected endpoints require a Bearer token in the `Authorization` header:
```http
Authorization: Bearer <access_token>
```

---

## 1. Authentication Endpoints (`/api/v1/auth`)

### POST `/api/v1/auth/register`
Creates a new candidate or recruiter account.
- **Access**: Public (Rate limit: 5 requests / hour)
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "StrongPassword123!",
    "full_name": "Alex Vance",
    "role": "candidate"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "c1f7b9e0-32df-4a67-9c98-123456789abc",
    "email": "user@example.com",
    "full_name": "Alex Vance",
    "role": "candidate",
    "is_active": true,
    "email_verified": false,
    "created_at": "2026-10-23T15:00:00Z"
  }
  ```

### POST `/api/v1/auth/login`
Authenticates a user and issues short-lived access and long-lived refresh tokens.
- **Access**: Public (Rate limit: 5 attempts / 15 minutes per IP/email)
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "StrongPassword123!"
  }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "refresh_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "bearer",
    "expires_in": 900
  }
  ```

### POST `/api/v1/auth/refresh`
Performs refresh-token rotation: verifies token hash, revokes old refresh token, and issues a new pair.
- **Access**: Public
- **Request Body**:
  ```json
  { "refresh_token": "eyJhbGciOiJIUzI1Ni..." }
  ```
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "refresh_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "bearer",
    "expires_in": 900
  }
  ```

### POST `/api/v1/auth/logout`
Revokes the provided refresh token in the database.
- **Access**: Public
- **Request Body**:
  ```json
  { "refresh_token": "eyJhbGciOiJIUzI1Ni..." }
  ```
- **Response (200 OK)**: `{"message": "Successfully logged out."}`

### POST `/api/v1/auth/forgot-password`
Initiates password reset; dispatches email or prints preview link to server console.
- **Request Body**: `{"email": "user@example.com"}`
- **Response (200 OK)**: `{"message": "If an account matches that email address, a password reset link has been dispatched."}`

### POST `/api/v1/auth/reset-password`
Resets password using a validated single-use token.
- **Request Body**:
  ```json
  {
    "token": "eyJhbGciOiJIUzI1Ni...",
    "new_password": "NewStrongPassword123!"
  }
  ```
- **Response (200 OK)**: `{"message": "Password has been successfully updated. You may now log in."}`

### GET `/api/v1/auth/me`
Returns current authenticated user profile.
- **Access**: Protected (Bearer token)
- **Response (200 OK)**: User profile object.

---

## 2. Resume Endpoints (`/api/v1/resumes`)

### POST `/api/v1/resumes/upload`
Uploads a PDF, DOCX, or TXT resume (max 5MB). Runs text extraction and Stage 2 Pydantic structuring.
- **Access**: Protected (Rate limit: 10 uploads / hour)
- **Content-Type**: `multipart/form-data`
- **Response (201 Created)**: Resume object with `extraction_status` and `structured_profile`.

### GET `/api/v1/resumes`
Lists all resumes owned by the authenticated user.
- **Parameters**: `skip` (default 0), `limit` (default 20).
- **Response (200 OK)**: `{"items": [...], "total": 2, "page": 1, "size": 20}`

### GET `/api/v1/resumes/{resume_id}`
Returns a specific resume profile.

### PATCH `/api/v1/resumes/{resume_id}`
Allows user to review and correct extracted fields.
- **Request Body**: `{"structured_profile": {...}}`

### DELETE `/api/v1/resumes/{resume_id}`
Soft-deletes resume and removes physical storage file.

### POST `/api/v1/resumes/{resume_id}/reparse`
Re-triggers document extraction and LLM structuring.

---

## 3. Job Endpoints (`/api/v1/jobs`)

### POST `/api/v1/jobs`
Creates a job from pasted text and triggers Stage 3 requirements extraction.
- **Request Body**:
  ```json
  {
    "title": "Junior Backend Developer",
    "company_name": "TechCorp",
    "raw_description": "We are looking for..."
  }
  ```
- **Response (201 Created)**: Job object with `structured_requirements`.

### POST `/api/v1/jobs/upload`
Uploads a job description document (PDF/DOCX/TXT).

### GET `/api/v1/jobs`
Lists user's saved jobs with optional search query (`?search=python`).

### GET `/api/v1/jobs/{job_id}`
Returns structured job posting by UUID.

### PATCH `/api/v1/jobs/{job_id}`
Updates job title, company name, or structured requirements.

### DELETE `/api/v1/jobs/{job_id}`
Soft-deletes the job posting.

### POST `/api/v1/jobs/{job_id}/analyze`
Re-runs AI requirement structuring for the job.

---

## 4. Matching Endpoints (`/api/v1/matches`)

### POST `/api/v1/matches`
Executes multi-stage matching pipeline between a selected resume and job.
- **Access**: Protected (Rate limit: 20 requests / hour)
- **Request Body**:
  ```json
  {
    "resume_id": "c1f7b9e0-32df-4a67-9c98-123456789abc",
    "job_id": "89f3a12b-7c4d-4567-89ab-987654321def"
  }
  ```
- **Response (201 Created)**:
  ```json
  {
    "id": "e3b0c442-98fc-1c14-9afb-4c8996fb9242",
    "overall_score": 88.5,
    "component_scores": {
      "required_skills": 92.0,
      "experience_relevance": 85.0,
      "nice_to_have_skills": 80.0,
      "projects_and_practical": 100.0,
      "education_fit": 100.0,
      "seniority_alignment": 95.0
    },
    "matched_skills": [
      {
        "skill": "Python",
        "resume_evidence": "Used in project 'Microservice Engine': Built cloud-native REST APIs.",
        "confidence": 1.0,
        "category": "required"
      }
    ],
    "missing_skills": [
      {
        "skill": "Kubernetes",
        "importance": "nice_to_have",
        "category": "nice_to_have"
      }
    ],
    "partial_skills": [],
    "explanation": "The candidate achieved an overall match score of 88.5/100...",
    "improvement_plan": {
      "missing_skills_ranked": [...],
      "learning_resources": [...],
      "project_ideas": [...]
    },
    "status": "completed"
  }
  ```

### GET `/api/v1/matches/{match_id}`
Returns full evaluation report.

### DELETE `/api/v1/matches/{match_id}`
Deletes match report.

---

## 5. Application Tracker Endpoints (`/api/v1/applications`)

### POST `/api/v1/applications`
Tracks an opportunity.
- **Request Body**:
  ```json
  {
    "job_id": "89f3a12b-7c4d-4567-89ab-987654321def",
    "resume_id": "c1f7b9e0-32df-4a67-9c98-123456789abc",
    "status": "applied",
    "notes": "Submitted referral via alumni network."
  }
  ```

### GET `/api/v1/applications/stats`
Returns application count breakdown by status (`saved`, `applied`, `screening`, `interview`, `technical_assessment`, `offer`, `rejected`, `withdrawn`).

### PATCH `/api/v1/applications/{application_id}`
Updates application stage, deadlines, or notes.

### DELETE `/api/v1/applications/{application_id}`
Removes application from tracking board.

---

## 6. Summary Endpoints (`/api/v1/summaries`)

### POST `/api/v1/summaries`
Generates a fact-verified professional summary connecting resume evidence to the target job description.
- **Request Body**: `{"resume_id": "...", "job_id": "..."}`
- **Response (201 Created)**: Tailored summary with verified quotes and unsupported flags.

---

## 7. Admin Endpoints (`/api/v1/admin`)

*Restricted to accounts with `admin` role.*

### GET `/api/v1/admin/metrics`
Platform KPI overview: total users, resumes processed, jobs analyzed, AI success rate, average latency, and top missing skills.

### GET `/api/v1/admin/ai-usage`
Paginated token usage, latency, and estimated cost logs.

### GET `/api/v1/admin/users`
User administration list. Note: Private resume raw text is masked to ensure privacy.

### PATCH `/api/v1/admin/users/{user_id}/status`
Activates or disables a user account (`{"is_active": false}`).

---

## 8. Health Check Endpoints

- `GET /health` &rarr; `{"status": "healthy", "service": "ResumeFit", "environment": "production"}`
- `GET /ready` &rarr; `{"ready": true, "database": "connected"}`
