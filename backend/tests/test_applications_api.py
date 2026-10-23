import pytest


@pytest.mark.asyncio
async def test_application_tracker_flow(client, auth_headers):
    # 1. Create a job first
    job_payload = {
        "title": "Software Engineer II",
        "company_name": "Acme Inc",
        "raw_description": "We are hiring a software engineer with full stack skills."
    }
    j_res = await client.post("/api/v1/jobs", json=job_payload, headers=auth_headers)
    job_id = j_res.json()["id"]

    # 2. Track application
    app_res = await client.post("/api/v1/applications", json={
        "job_id": job_id,
        "status": "applied",
        "notes": "Submitted application via referral."
    }, headers=auth_headers)
    assert app_res.status_code == 201
    app_data = app_res.json()
    app_id = app_data["id"]
    assert app_data["status"] == "applied"
    assert app_data["job"]["title"] == "Software Engineer II"

    # 3. Check stats
    stats_res = await client.get("/api/v1/applications/stats", headers=auth_headers)
    assert stats_res.status_code == 200
    assert stats_res.json()["total_applications"] >= 1
    assert stats_res.json()["by_status"]["applied"] >= 1

    # 4. Patch status
    patch_res = await client.patch(f"/api/v1/applications/{app_id}", json={
        "status": "interview",
        "notes": "First round behavioral scheduled."
    }, headers=auth_headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "interview"

    # 5. List applications
    list_res = await client.get("/api/v1/applications", headers=auth_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 6. Delete application
    del_res = await client.delete(f"/api/v1/applications/{app_id}", headers=auth_headers)
    assert del_res.status_code == 200
