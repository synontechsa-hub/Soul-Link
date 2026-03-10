# /backend/tests/test_load.py
# v1.5.5 - Load Testing (50 Concurrent Users)

import pytest
import asyncio
import time
from httpx import AsyncClient
from backend.app.main import app
from backend.app.api.dependencies import get_current_user
from backend.app.models.user import User

# Sample User IDs for load simulation
USER_IDS = [f"user_load_{i}" for i in range(50)]

@pytest.fixture
def mock_users():
    """Disable rate limiting for load testing if needed, or set up multiple users."""
    # For load testing, we override the user dependency to rotate through users
    # but for a simple "system stress" test, we can just use a generic user
    # or handle the rotation inside the test loop.
    pass

async def simulate_user_request(client: AsyncClient, user_id: str):
    """Simulates a single user's request pattern."""
    # Override user for this specific request context if possible? 
    # Actually, dependency_overrides is global. 
    # To simulate DIFFERENT users, we might need a more complex approach,
    # but for RAW LOAD on the engine, hitting /world-state is sufficient.
    
    start_time = time.perf_counter()
    try:
        # Hit world state (heavy read)
        response = await client.get("/api/v1/map/world-state")
        latency = time.perf_counter() - start_time
        return response.status_code, latency
    except Exception as e:
        return 500, 0

@pytest.mark.asyncio
async def test_load_50_concurrent_users(client: AsyncClient, async_session):
    """
    Fire 50 concurrent requests to /locations and check latency/stability.
    """
    # Seed data so the request actually does work
    from backend.app.models.location import Location
    from backend.app.models.soul import Soul
    from backend.app.models.user import User
    from datetime import datetime

    # Create the test user in DB
    test_user = User(
        user_id="load_test_architect",
        username="load_test",
        display_name="Load Test Architect",
        account_tier="architect",
        current_location="loc_0",
        current_time_slot="morning",
        gems=0,
        energy=100,
        lifetime_tokens_used=0,
        total_ads_watched=0,
        created_at=datetime.utcnow(),
        last_energy_refill=datetime.utcnow()
    )
    async_session.add(test_user)

    for i in range(5):
        async_session.add(Location(
            location_id=f"loc_{i}",
            display_name=f"Location {i}",
            music_track="theme",
            min_intimacy=0
        ))
        async_session.add(Soul(
            soul_id=f"soul_{i}",
            name=f"Soul {i}",
            summary="Load test soul",
            portrait_url="http://test.com",
            version="1.0",
            created_at=datetime.utcnow()
        ))
    await async_session.commit()
    await async_session.refresh(test_user)

    # Override user to use the one we just created
    async def get_mock_user():
        return test_user
    app.dependency_overrides[get_current_user] = get_mock_user
    
    # Disable rate limiter for load test
    from backend.app.core.rate_limiter import limiter
    limiter.enabled = False
    
    # Pre-warm cache
    print(f"\n[WARM] Pre-warming cache...")
    await client.get("/api/v1/map/locations")
    
    tasks = []
    for i in range(50):
        tasks.append(client.get("/api/v1/map/locations"))
    
    print(f"\n[START] Launching 50 concurrent requests to /locations...")
    start_test = time.perf_counter()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.perf_counter() - start_test
    
    print(f"[METRICS] Results:")
    status_codes = []
    latencies = []
    errors = []
    
    for r in results:
        if isinstance(r, Exception):
            errors.append(str(r))
            status_codes.append(500)
            latencies.append(0)
        else:
            status_codes.append(r.status_code)
            latencies.append(r.elapsed.total_seconds())
    
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    success_count = status_codes.count(200)
    
    print(f"  - Total Time: {total_time:.4f}s")
    print(f"  - Avg Latency: {avg_latency:.4f}s")
    print(f"  - Max Latency: {max(latencies) if latencies else 0:.4f}s")
    print(f"  - Success Rate: {success_count}/50")
    if errors:
        print(f"  - Errors encountered: {len(errors)}")
        for e in errors[:5]: # Show first 5
            print(f"    - {e}")
    
    # Assertions
    assert success_count == 50, f"Only {success_count}/50 requests succeeded"
    assert avg_latency < 1.0, f"Average latency too high: {avg_latency:.4f}s"
    
    app.dependency_overrides.clear()
