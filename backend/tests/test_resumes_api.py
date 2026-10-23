import io
import pytest


@pytest.mark.asyncio
async def test_resume_upload_and_lifecycle(client, auth_headers):
    # 1. Upload TXT resume
    sample_text = (
        "John Doe\njohn@example.com\nSoftware Engineer\n\n"
        "Skills: Python, FastAPI, Docker, PostgreSQL, React\n\n"
        "Projects:\n"
        "Project: Microservice Engine\n"
        "Built cloud-native REST APIs using Python, Docker, and PostgreSQL.\n\n"
        "Education: Bachelor of Science in Computer Science, 2024"
    )
    files = {"file": ("john_resume.txt", io.BytesIO(sample_text.encode("utf-8")), "text/plain")}

    upload_res = await client.post("/api/v1/resumes/upload", files=files, headers=auth_headers)
    assert upload_res.status_code == 201
    resume_data = upload_res.json()
    resume_id = resume_data["id"]
    assert resume_data["original_filename"] == "john_resume.txt"
    assert resume_data["extraction_status"] in ["completed", "processing"]

    # 2. Get resume by ID
    get_res = await client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == resume_id

    # 3. List resumes
    list_res = await client.get("/api/v1/resumes", headers=auth_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # 4. Patch resume profile
    patch_res = await client.patch(
        f"/api/v1/resumes/{resume_id}",
        json={"structured_profile": {"skills": ["Python", "FastAPI", "Kubernetes"]}},
        headers=auth_headers
    )
    assert patch_res.status_code == 200
    assert "Kubernetes" in patch_res.json()["structured_profile"]["skills"]

    # 5. Delete resume
    del_res = await client.delete(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert del_res.status_code == 200

    # 6. Verify 404 after delete
    get_del_res = await client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert get_del_res.status_code == 404


@pytest.mark.asyncio
async def test_resume_upload_size_limit(client, auth_headers):
    # Exceed 5MB limit
    big_content = b"0" * (6 * 1024 * 1024)
    files = {"file": ("huge_resume.txt", io.BytesIO(big_content), "text/plain")}

    upload_res = await client.post("/api/v1/resumes/upload", files=files, headers=auth_headers)
    assert upload_res.status_code == 400
