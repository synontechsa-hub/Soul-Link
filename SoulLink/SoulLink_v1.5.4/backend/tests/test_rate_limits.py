
import pytest
from httpx import AsyncClient
import asyncio

@pytest.mark.asyncio
async def test_global_rate_limit(client: AsyncClient, mock_auth):
    """
    Test that the rate limiter blocks requests after exceeding the threshold.
    Target: /api/v1/users/me (Scope: READ_ONLY = 100/minute)
    """
    endpoint = "/api/v1/users/me"
    
    # Send enough requests to trigger the limit (100 + buffer)
    # Since tests run fast, we might hit the limit quickly.
    requests_to_send = 110
    
    # We use gather to send them concurrently, modeling a burst
    tasks = [client.get(endpoint) for _ in range(requests_to_send)]
    responses = await asyncio.gather(*tasks)
    
    # Check if we got any 429s
    status_codes = [r.status_code for r in responses]
    
    # We expect mostly 200s, then 429s.
    assert 429 in status_codes, f"Did not trigger rate limit! Codes: {status_codes[:10]}..."
    
    # Verify the error message format (ensure no header injection crash)
    error_resp = next(r for r in responses if r.status_code == 429)
    data = error_resp.json()
    assert data["status"] == "error"
    assert "Neural Link Overloaded" in data["message"]
