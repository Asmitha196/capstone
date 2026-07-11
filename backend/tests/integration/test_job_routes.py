"""
Integration tests for FastAPI job routes.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_jobs_empty(client: AsyncClient) -> None:
    """Test retrieving job listings when database is empty."""
    response = await client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0
    assert data["skip"] == 0
    assert data["limit"] == 20


@pytest.mark.asyncio
async def test_create_job_unauthorized(client: AsyncClient) -> None:
    """Test job creation fails without JWT token authorization."""
    payload = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "description": "Develop features using FastAPI and React.",
    }
    response = await client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_and_manage_job_flow(client: AsyncClient) -> None:
    """Test full flow: register -> login -> create job -> list -> update -> get -> delete."""
    # 1. Register & Login
    register_payload = {
        "email": "job_admin@example.com",
        "password": "SecurePassword123",
        "full_name": "Job Publisher",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "job_admin@example.com",
        "password": "SecurePassword123",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Job
    job_payload = {
        "title": "Python Developer",
        "company": "AI Innovators",
        "location": "San Francisco, CA",
        "job_type": "full-time",
        "experience_level": "mid",
        "salary_min": 100000.0,
        "salary_max": 140000.0,
        "currency": "USD",
        "description": "Looking for a mid-level Python developer experienced in FastAPI.",
        "requirements": "3+ years Python, FastAPI experience.",
        "benefits": "Health insurance, equity.",
        "skills_required": "Python,FastAPI,SQLAlchemy",
        "apply_url": "https://example.com/apply",
    }
    create_res = await client.post("/api/v1/jobs", json=job_payload, headers=headers)
    assert create_res.status_code == 201
    job_data = create_res.json()
    assert job_data["title"] == "Python Developer"
    assert job_data["company"] == "AI Innovators"
    assert job_data["skills_required"] == ["Python", "FastAPI", "SQLAlchemy"]
    job_id = job_data["id"]

    # 3. List Jobs with search
    list_res = await client.get("/api/v1/jobs?search=Python")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["id"] == job_id

    # 4. Get Job by ID
    get_res = await client.get(f"/api/v1/jobs/{job_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Python Developer"

    # 5. Update Job
    update_payload = {
        "title": "Senior Python Developer",
        "salary_min": 120000.0,
        "skills_required": ["Python", "FastAPI", "SQLAlchemy", "Docker"],
    }
    update_res = await client.put(f"/api/v1/jobs/{job_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["title"] == "Senior Python Developer"
    assert updated_data["salary_min"] == 120000.0
    assert updated_data["skills_required"] == ["Python", "FastAPI", "SQLAlchemy", "Docker"]

    # 6. Delete Job
    delete_res = await client.delete(f"/api/v1/jobs/{job_id}", headers=headers)
    assert delete_res.status_code == 200

    # 7. Verify deletion
    get_after_delete = await client.get(f"/api/v1/jobs/{job_id}")
    assert get_after_delete.status_code == 404
