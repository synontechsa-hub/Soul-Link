# /backend/tests/test_health.py
# v1.5.5 - Health Check Tests

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """
    Test that the health check endpoint returns 200 and correct structure.
    """
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "checks" in data
    assert data["checks"]["database"] == "ok"
    assert "websocket" in data["checks"]

@pytest.mark.asyncio
async def test_readiness_probe(client: AsyncClient):
    """
    Test kubernetes readiness probe.
    """
    response = await client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient):
    """
    Test metrics endpoint structure.
    """
    response = await client.get("/api/v1/health/metrics")
    assert response.status_code == 200
    
    data = response.json()
    assert "websocket" in data
    assert "database" in data
    assert "system" in data
    assert data["system"]["cpu_percent"] >= 0
