
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_ping(client: AsyncClient):
    """Verify that root path returns 200 (as it's the engine status page)."""
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Verify that protected endpoints require authentication."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_authorized_access_mock(client: AsyncClient, mock_auth):
    """Verify that the mock authentication fixture works and endpoint returns success."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == "TestArchitect"
    assert data["account_tier"] == "architect"


@pytest.mark.asyncio
async def test_user_profile_includes_active_persona_id(client: AsyncClient, mock_auth):
    """Verify /users/me response always includes active_persona_id (even if null).

    Regression guard: UserProfile schema previously omitted this field,
    causing the frontend persona system to always read null.
    """
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 200

    data = response.json()
    # Key must be present — value may be null for users without an active persona
    assert "active_persona_id" in data
