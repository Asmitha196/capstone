"""
Integration tests for FastAPI authentication routes.
Uses async HTTPX client to test endpoints and verify headers, payload structure, and route authorization.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_route_register_success(client: AsyncClient) -> None:
    """Test POST /api/v1/auth/register endpoint."""
    payload = {
        "email": "route_register@example.com",
        "password": "SecurePassword123",
        "full_name": "Route Registered User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "route_register@example.com"
    assert data["full_name"] == "Route Registered User"
    assert "id" in data
    assert "hashed_password" not in data  # password hash must never be returned


@pytest.mark.asyncio
async def test_route_register_invalid_data(client: AsyncClient) -> None:
    """Test registration endpoint with weak/invalid password validation."""
    payload = {
        "email": "invalid_pass@example.com",
        "password": "weak",  # too short, no number, no uppercase
        "full_name": "No User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_route_login_and_me_success(client: AsyncClient) -> None:
    """Test login flow and subsequent /me profile retrieval using the access token."""
    # 1. Register
    register_payload = {
        "email": "login_me@example.com",
        "password": "SecurePassword123",
        "full_name": "Login Me User",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    # 2. Login
    login_payload = {
        "email": "login_me@example.com",
        "password": "SecurePassword123",
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == 200
    token_data = login_response.json()
    
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"
    
    access_token = token_data["access_token"]

    # 3. Retrieve profile /me
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = await client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    profile_data = me_response.json()
    assert profile_data["email"] == "login_me@example.com"
    assert profile_data["full_name"] == "Login Me User"


@pytest.mark.asyncio
async def test_route_me_unauthorized(client: AsyncClient) -> None:
    """Test GET /api/v1/auth/me returns 401 when request lacks authorization header."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert "Bearer" in response.headers.get("WWW-Authenticate", "")


@pytest.mark.asyncio
async def test_route_refresh_token(client: AsyncClient) -> None:
    """Test POST /api/v1/auth/refresh to retrieve a fresh token pair."""
    # 1. Register & Login
    register_payload = {
        "email": "refresh_test@example.com",
        "password": "SecurePassword123",
        "full_name": "Refresh User",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "refresh_test@example.com",
        "password": "SecurePassword123",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    tokens = login_res.json()
    refresh_token = tokens["refresh_token"]

    # 2. Refresh tokens
    refresh_response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens


@pytest.mark.asyncio
async def test_route_logout(client: AsyncClient) -> None:
    """Test POST /api/v1/auth/logout blacklists token and prevents subsequent access."""
    # 1. Register & Login
    register_payload = {
        "email": "logout_test@example.com",
        "password": "SecurePassword123",
        "full_name": "Logout User",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "logout_test@example.com",
        "password": "SecurePassword123",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    access_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Call /me to confirm it works
    me_before = await client.get("/api/v1/auth/me", headers=headers)
    assert me_before.status_code == 200

    # 3. Logout
    logout_response = await client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 204

    # 4. Try /me again — should be blacklisted and unauthorized
    me_after = await client.get("/api/v1/auth/me", headers=headers)
    assert me_after.status_code == 401


@pytest.mark.asyncio
async def test_route_update_profile(client: AsyncClient) -> None:
    """Test PUT /api/v1/auth/me updates profile details successfully."""
    # 1. Register & Login
    register_payload = {
        "email": "update_me@example.com",
        "password": "SecurePassword123",
        "full_name": "Original Name",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "update_me@example.com",
        "password": "SecurePassword123",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    access_token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Update Profile
    update_payload = {
        "full_name": "Updated Name",
        "headline": "Senior React Engineer",
        "location": "Boston, MA",
        "bio": "AI engineering student and developer",
        "years_of_experience": 4,
    }
    update_res = await client.put("/api/v1/auth/me", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    
    data = update_res.json()
    assert data["full_name"] == "Updated Name"
    assert data["headline"] == "Senior React Engineer"
    assert data["location"] == "Boston, MA"
    assert data["bio"] == "AI engineering student and developer"
    assert data["years_of_experience"] == 4

