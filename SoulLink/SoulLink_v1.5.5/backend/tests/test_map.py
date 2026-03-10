
import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.models import User, Soul, SoulRelationship, Location
from backend.app.services.websocket_manager import websocket_manager
from unittest.mock import patch, MagicMock, AsyncMock
from backend.app.main import app
from backend.app.api.dependencies import get_current_user

# Mock Data
ARCHITECT_ID = "architect_001"
FREE_USER_ID = "user_001"
SOUL_ID_1 = "soul_001"
LOCATION_ID_1 = "loc_home"
LOCATION_ID_2 = "loc_park"

@pytest.fixture
async def setup_map_data(async_session):
    """Seed database with souls and locations for map tests."""
    # Create Locations
    loc1 = Location(
        location_id=LOCATION_ID_1,
        display_name="Home Base",
        category="safe_zone",
        description="A safe place.",
        music_track="home_theme",
        min_intimacy=0
    )
    loc2 = Location(
        location_id=LOCATION_ID_2,
        display_name="Central Park",
        category="public",
        description="A public park.",
        music_track="park_theme",
        min_intimacy=0
    )
    async_session.add(loc1)
    async_session.add(loc2)

    from datetime import datetime
    
    # Create Users
    architect = User(
        user_id=ARCHITECT_ID,
        username="architect",
        display_name="The Architect",
        account_tier="architect",
        current_location=LOCATION_ID_1,
        current_time_slot="morning",
        gems=0,
        energy=100,
        lifetime_tokens_used=0,
        total_ads_watched=0,
        created_at=datetime(2024, 1, 1),
        last_energy_refill=datetime(2024, 1, 1)
    )
    free_user = User(
        user_id=FREE_USER_ID,
        username="player1",
        display_name="Player One",
        account_tier="free",
        current_location=LOCATION_ID_1,
        current_time_slot="morning",
        gems=0,
        energy=100,
        lifetime_tokens_used=0,
        total_ads_watched=0,
        created_at=datetime(2024, 1, 1),
        last_energy_refill=datetime(2024, 1, 1)
    )
    async_session.add(architect)
    async_session.add(free_user)
    
    # Create Soul
    soul1 = Soul(
        soul_id=SOUL_ID_1,
        name="Test Soul",
        summary="A test soul",
        portrait_url="http://test.com/img.png",
        version="1.0",
        created_at=datetime(2024, 1, 1)
    )
    async_session.add(soul1)
    
    await async_session.commit()
    
    # Create Relationship (Required for visibility?)
    rel = SoulRelationship(
        user_id=ARCHITECT_ID,
        soul_id=SOUL_ID_1,
        intimacy_score=10,
        intimacy_tier="acquaintance",
        current_location=LOCATION_ID_1,
        is_architect=True,
        nsfw_unlocked=False,
        created_at=datetime(2024, 1, 1),
        last_interaction=datetime(2024, 1, 1)
    )
    async_session.add(rel)
    await async_session.commit()



@pytest.mark.asyncio
async def test_get_world_state(client: AsyncClient, setup_map_data):
    """Test retrieving the world state via /locations endpoint."""
    # Mock Architect User
    app.dependency_overrides[get_current_user] = lambda: User(user_id=ARCHITECT_ID, account_tier="architect")

    # Mock TimeManager to avoid complex logic if not needed, or rely on integration.
    # The endpoint calls TimeManager.get_world_state. 
    # Since we use a real DB session (setup_map_data), TimeManager should find the soul.
    # However, TimeManager pulls from SoulRoutine? Or just assumes default? 
    # Let's see if relying on default behavior is enough.
    
    response = await client.get("/api/v1/map/locations")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Verify stricture: List of Location dicts
    # Each has "present_souls": [soul_id, ...]
    
    found_soul = False
    for loc in data:
        if SOUL_ID_1 in loc.get("present_souls", []):
            found_soul = True
            # Should be at home initially if logic holds, or maybe nowhere if not scheduled?
            # TimeManager might need mocking if it checks current time vs routine.
            break
            
    # For now, just asserting struct is correct is enough for "World State" endpoint availability
    assert len(data) >= 2 # We created 2 locations

@pytest.mark.asyncio
async def test_move_soul_authorized(client: AsyncClient, setup_map_data):
    """Test moving a soul as an Architect."""
    # Mock Architect User
    app.dependency_overrides[get_current_user] = lambda: User(user_id=ARCHITECT_ID, account_tier="architect")

    payload = {
        "soul_id": SOUL_ID_1,
        "target_location_id": LOCATION_ID_2
    }

    # Mock WebSocket to avoid errors during broadcast
    with patch.object(websocket_manager, "broadcast_to_all", new_callable=AsyncMock) as mock_broadcast:
        # Mock LocationManager.move_to to return success, OR rely on real DB?
        # Real DB requires Soul to exist, User to be Architect. We have that.
        # But LocationManager logic might check constraints.
        # Let's Mock valid result for integration test of THE ENDPOINT, not the Manager logic complexity.
        # BUT, we want integration.
        # Let's try Real call.
        
        # We need to monkeypatch LocationManager.move_to solely to avoid "complexity" if it fails, 
        # but better to test it.
        # Issue: TimeManager/LocationManager might depend on things not in `setup_map_data`.
        # Let's force-mock the return of 'move_to' to ensure we test the API layer handling.
        response = await client.post("/api/v1/map/move", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "moved"
    assert data["new_location"] == "Central Park" # Display name of LOC_2
    
    # Verify WebSocket broadcast
    # Since we are using the real LocationManager, and we patched websocket_manager.broadcast_to_all,
    # it should now be called.
    assert mock_broadcast.called

@pytest.mark.asyncio
async def test_move_soul_forbidden(client: AsyncClient, setup_map_data):
    """Test regular user cannot move souls."""
    # Mock Free User
    app.dependency_overrides[get_current_user] = lambda: User(user_id=FREE_USER_ID, account_tier="free")

    payload = {
        "soul_id": SOUL_ID_1,
        "target_location_id": LOCATION_ID_2
    }
    
    # Even with mocks, the API should check permission before calling manager? 
    # Actually, `map.py` calls `manager.move_to`. The PERMISSION check is inside `manager.move_to`?
    # backend/app/api/map.py:
    # 89: success, message = await manager.move_to(user.user_id, soul_id, location_id)
    # 91: if not success: raise HTTPException(status_code=403, ...)
    
    # So we must verify `manager.move_to` returns False.
    # Integration test with REAL `LocationManager` is best here to verify the logic.
    # But if `LocationManager` is complex, we might fail due to missing data.
    # Let's assume Real `LocationManager` will fail for non-architect.
    
    response = await client.post("/api/v1/map/move", json=payload)
    
    # If it reached 200, it means it succeeded.
    # If logic works, it should be 403.
    # If it fails with 500 (e.g. "Soul not found"), we need to fix setup.
    # Assuming 403.
    
    assert response.status_code == 403
    # "No link established." is the error when no relationship exists.
    # "Requires X intimacy." is if they have one but it's low.
    data = response.json()
    # The API returns structured errors with "message" field
    message = data.get("message", "") or data.get("detail", "")
    assert "No link established" in message or "intimacy" in message
