"""
Integration tests for FastAPI RAG routes.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rag_routes_unauthorized(client: AsyncClient) -> None:
    """Test all RAG endpoints fail without JWT authorization."""
    response = await client.post("/api/v1/rag/embed-jobs")
    assert response.status_code == 401

    response = await client.post("/api/v1/rag/search", json={"query": "Python", "limit": 2})
    assert response.status_code == 401

    response = await client.post("/api/v1/rag/ask", json={"question": "What roles require Python?"})
    assert response.status_code == 401

    response = await client.post("/api/v1/rag/analyse-resume", json={"resume_text": "A resume text."})
    assert response.status_code == 401

    response = await client.post("/api/v1/rag/job-match", json={"resume_text": "Resume text", "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_rag_full_flow(client: AsyncClient) -> None:
    """Test full RAG lifecycle: seed job -> embed-jobs -> search -> ask -> job-match -> analyse-resume."""
    # 1. Register & Login to get token
    register_payload = {
        "email": "rag_user@example.com",
        "password": "SecurePassword123",
        "full_name": "RAG Master",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "rag_user@example.com",
        "password": "SecurePassword123",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Seed a Job Listing
    job_payload = {
        "title": "Django Developer",
        "company": "Django Wizards",
        "location": "Remote",
        "job_type": "full-time",
        "experience_level": "senior",
        "salary_min": 130000.0,
        "salary_max": 160000.0,
        "description": "Looking for a Python developer with Django and PostgreSQL expertise to build REST APIs.",
        "requirements": "5+ years Python development.",
        "skills_required": "Python,Django,PostgreSQL,Rest API",
        "apply_url": "https://example.com/apply-django",
    }
    job_res = await client.post("/api/v1/jobs", json=job_payload, headers=headers)
    assert job_res.status_code == 201
    job_data = job_res.json()
    job_id = job_data["id"]

    # 3. Embed Jobs (trigger RAG indexing)
    embed_res = await client.post("/api/v1/rag/embed-jobs", headers=headers)
    assert embed_res.status_code == 200
    assert embed_res.json()["jobs_embedded"] >= 1

    # 4. Search jobs via vector search
    search_payload = {"query": "Django", "limit": 2}
    search_res = await client.post("/api/v1/rag/search", json=search_payload, headers=headers)
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert len(search_data["items"]) >= 1
    assert search_data["items"][0]["job"]["id"] == job_id
    assert "score" in search_data["items"][0]

    # 5. Ask Questions using job context
    ask_payload = {"question": "What databases are required for the Django Developer role?"}
    ask_res = await client.post("/api/v1/rag/ask", json=ask_payload, headers=headers)
    assert ask_res.status_code == 200
    assert "answer" in ask_res.json()
    assert len(ask_res.json()["context_jobs"]) >= 1

    # 6. Job Matching
    match_payload = {
        "resume_text": "Senior Developer with 8 years of Python experience developing API backends with Django and PostgreSQL.",
        "job_id": job_id,
    }
    match_res = await client.post("/api/v1/rag/job-match", json=match_payload, headers=headers)
    assert match_res.status_code == 200
    match_data = match_res.json()
    assert match_data["match_score"] > 0
    assert "Django" in match_data["matching_skills"]
    assert "explanation" in match_data

    # 7. Analyse resume using RAG
    analyse_payload = {
        "resume_text": "Experienced engineer with skills in Python, Git, and PostgreSQL. Seeking a backend developer role."
    }
    analyse_res = await client.post("/api/v1/rag/analyse-resume", json=analyse_payload, headers=headers)
    assert analyse_res.status_code == 200
    analyse_data = analyse_res.json()
    assert "extracted_skills" in analyse_data
    assert "missing_skills" in analyse_data
