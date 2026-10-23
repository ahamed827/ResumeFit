import pytest


@pytest.mark.asyncio
async def test_job_create_and_lifecycle(client, auth_headers):
    # 1. Create job from pasted text
    job_payload = {
        "title": "Junior Python Developer",
        "company_name": "Tech Corp",
        "raw_description": (
            "We are seeking a Junior Python Developer.\n"
            "Requirements:\n"
            "- Strong proficiency in Python, FastAPI, and SQL.\n"
            "- Experience with Docker and Git is nice to have.\n"
            "- Bachelor's degree in Computer Science or equivalent.\n"
            "Responsibilities: Write tested backend code and maintain API documentation."
        )
    }

    create_res = await client.post("/api/v1/jobs", json=job_payload, headers=auth_headers)
    assert create_res.status_code == 201
    job_data = create_res.json()
    job_id = job_data["id"]
    assert job_data["title"] == "Junior Python Developer"
    assert job_data["company_name"] == "Tech Corp"
    assert job_data["analysis_status"] in ["completed", "processing"]

    # 2. Get job by ID
    get_res = await client.get(f"/api/v1/jobs/{job_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == job_id

    # 3. List jobs
    list_res = await client.get("/api/v1/jobs", headers=auth_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 4. Patch job
    patch_res = await client.patch(
        f"/api/v1/jobs/{job_id}",
        json={"title": "Software Engineer I - Python"},
        headers=auth_headers
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Software Engineer I - Python"

    # 5. Delete job
    del_res = await client.delete(f"/api/v1/jobs/{job_id}", headers=auth_headers)
    assert del_res.status_code == 200
