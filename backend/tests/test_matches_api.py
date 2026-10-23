import io
import pytest


@pytest.mark.asyncio
async def test_match_creation_and_ownership(client, auth_headers):
    # 1. Upload Resume
    resume_text = (
        "Candidate Resume\n"
        "Skills: Python, FastAPI, Docker, PostgreSQL\n"
        "Education: Bachelor of Science in Computer Science\n"
        "Projects: Built API backend in Python and PostgreSQL"
    )
    files = {"file": ("cand.txt", io.BytesIO(resume_text.encode("utf-8")), "text/plain")}
    r_res = await client.post("/api/v1/resumes/upload", files=files, headers=auth_headers)
    resume_id = r_res.json()["id"]

    # 2. Create Job
    job_payload = {
        "title": "Backend Python Engineer",
        "company_name": "Innovate",
        "raw_description": "Seeking Backend Engineer proficient in Python, FastAPI, and Docker. Bachelor degree preferred."
    }
    j_res = await client.post("/api/v1/jobs", json=job_payload, headers=auth_headers)
    job_id = j_res.json()["id"]

    # 3. Create Match
    match_res = await client.post("/api/v1/matches", json={
        "resume_id": resume_id,
        "job_id": job_id
    }, headers=auth_headers)
    assert match_res.status_code == 201
    match_data = match_res.json()
    match_id = match_data["id"]

    assert match_data["overall_score"] is not None
    assert 0 <= match_data["overall_score"] <= 100
    assert "component_scores" in match_data
    assert len(match_data["matched_skills"]) > 0

    # 4. Get Match
    get_match_res = await client.get(f"/api/v1/matches/{match_id}", headers=auth_headers)
    assert get_match_res.status_code == 200
    assert get_match_res.json()["id"] == match_id

    # 5. List Matches
    list_res = await client.get("/api/v1/matches", headers=auth_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1
