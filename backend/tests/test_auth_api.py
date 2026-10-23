import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    res = await client.post("/api/v1/auth/register", json={
        "email": "fresh_user@example.com",
        "password": "Password123!",
        "full_name": "Fresh Candidate",
        "role": "candidate"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "fresh_user@example.com"
    assert data["full_name"] == "Fresh Candidate"
    assert data["role"] == "candidate"


@pytest.mark.asyncio
async def test_register_duplicate_conflict(client, test_user):
    res = await client.post("/api/v1/auth/register", json={
        "email": test_user.email,
        "password": "Password123!",
        "full_name": "Another User",
        "role": "candidate"
    })
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_login_success_and_refresh_rotation(client, test_user):
    # Login
    res = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "ValidPass123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

    old_refresh = data["refresh_token"]

    # Refresh
    refresh_res = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": old_refresh
    })
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data

    # Old refresh token should now be revoked (rotation)
    reused_res = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": old_refresh
    })
    assert reused_res.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_credentials(client, test_user):
    res = await client.post("/api/v1/auth/login", json={
        "email": test_user.email,
        "password": "IncorrectPassword!"
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_profile(client, auth_headers):
    # With valid token
    res = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "candidate@test.com"

    # Without token
    unauth_res = await client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401
