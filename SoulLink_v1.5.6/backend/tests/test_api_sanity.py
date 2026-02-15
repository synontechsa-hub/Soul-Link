
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
