"""
Integration tests for FastAPI resume analysis routes.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_resume_unauthorized(client: AsyncClient) -> None:
    """Test resume analysis request fails without JWT authorization."""
    payload = {
        "resume_text": "Experienced software developer with skill sets in Python, React, and git.",
    }
    response = await client.post("/api/v1/resume/analyze", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_analyze_resume_success(client: AsyncClient) -> None:
    """Test successful resume analysis flow."""
    # 1. Register & Login to get token
    register_payload = {
        "email": "resume_user@example.com",
        "password": "SecurePassword123",
        "full_name": "Resume Owner",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "resume_user@example.com",
        "password": "SecurePassword123",
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Analyze Resume
    resume_text = (
        "Experienced software developer. Technical skills: Python, Javascript, git, and PostgreSQL. "
        "Worked as a Senior developer for 5 years leading a team of 4 engineers building backend services."
    )
    analysis_payload = {
        "resume_text": resume_text,
        "target_job_title": "React and FastAPI Developer",
        "target_job_description": "Build high performance user interfaces using React and backends using FastAPI.",
    }

    response = await client.post("/api/v1/resume/analyze", json=analysis_payload, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "extracted_skills" in data
    assert "experience" in data
    assert "missing_skills" in data
    assert "recommendations" in data

    # Verify matching heuristics
    assert "Python" in data["extracted_skills"]
    assert "PostgreSQL" in data["extracted_skills"]
    assert "React" in data["missing_skills"]
    assert "FastAPI" in data["missing_skills"]
    assert len(data["recommendations"]) > 0
    assert any(keyword in data["recommendations"][0] for keyword in ["React", "FastAPI", "role", "developer"])
