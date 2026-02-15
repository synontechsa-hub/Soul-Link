# /backend/tests/test_chat.py
# v1.5.5 - Chat API Integration Tests

import pytest
from httpx import AsyncClient
from backend.app.models import User, Soul, SoulRelationship, SoulPillar, SoulState
from backend.app.services.websocket_manager import websocket_manager
from unittest.mock import patch, MagicMock, AsyncMock

# Mock user data
TEST_USER_ID = "test_user_123"
TEST_SOUL_ID = "soul_001"

@pytest.fixture
async def setup_chat_data(async_session):
    """Seed database with test user, soul, and relationship."""
    try:
        # 1. Create User
        user = User(user_id=TEST_USER_ID, username="Tester", account_tier="architect")
        async_session.add(user)
        
        # 2. Create Soul (Must be committed for FKs to work)
        # Note: soul_id is the primary key, but we also pass it as kwarg for safety if model definition is redundant
        # We explicitly set BOTH to ensure SQLAlchemy maps it correctly for FKs
        soul = Soul(id=TEST_SOUL_ID, soul_id=TEST_SOUL_ID, name="Test Soul", slug="test-soul")
        async_session.add(soul)
        await async_session.commit() # Commit parent first
        
        # 3. Create Pillar (Required for Logic)
        pillar = SoulPillar(soul_id=TEST_SOUL_ID, name="Logic Core", routines={})
        async_session.add(pillar)
        
        # 4. Create State (Required for Location)
        # Note: current_location_id="soul_plaza" is the default and usually safe, 
        # but if locations table has FK, we might need to seed it too.
        # For now, let's assume "soul_plaza" is safe or there's no FK on this field yet.
        state = SoulState(soul_id=TEST_SOUL_ID, current_location_id="soul_plaza")
        async_session.add(state)
        
        # 5. Create Relationship
        rel = SoulRelationship(
            user_id=TEST_USER_ID, 
            soul_id=TEST_SOUL_ID,
            intimacy_score=50,
            intimacy_tier="acquaintance"
        )
        async_session.add(rel)
        
        await async_session.commit()
    except Exception as e:
        await async_session.rollback()
        raise e

@pytest.mark.asyncio
async def test_send_chat_message(client: AsyncClient, setup_chat_data, async_session):
    """
    Test sending a valid chat message.
    Mocks the Brain and Supabase auth.
    """
    
    # Mock Brain response
    with patch("backend.app.logic.brain.LegionBrain.generate_response") as mock_brain:
        mock_brain.return_value = "This is a mock response."
        
        # Mock Supabase Auth (Override Dependency)
        from backend.app.api.dependencies import get_current_user
        from backend.app.main import app
        
        # Define mock user that matches seeded data
        mock_user = User(user_id=TEST_USER_ID, username="Tester", account_tier="architect")
        
        # Override to return our mock user directly (bypassing DB lookup in dependent tests)
        app.dependency_overrides[get_current_user] = lambda: mock_user
        
        # Mock WebSocket manager 
        with patch.object(websocket_manager, "send_to_user", new_callable=AsyncMock) as mock_ws:
            payload = {
                "soul_id": TEST_SOUL_ID,
                "message": "Hello, world!"
            }
            
            response = await client.post("/api/v1/chat/send", json=payload)
            
            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "This is a mock response."
            assert data["soul_id"] == TEST_SOUL_ID
            assert data["intimacy_score"] == 50
            
            # Verify WebSocket was called (Real-time update)
            assert mock_ws.called


@pytest.mark.asyncio
async def test_chat_invalid_soul(client: AsyncClient):
    """Test sending message to non-existent soul."""
    
    # Mock Auth
    from backend.app.api.dependencies import get_current_user
    from backend.app.main import app
    app.dependency_overrides[get_current_user] = lambda: User(user_id=TEST_USER_ID, account_tier="free")
    
    payload = {
        "soul_id": "non_existent_soul",
        "message": "Hello?"
    }
    
    response = await client.post("/api/v1/chat/send", json=payload)
    
    # Process might vary depending on implementation (404 or 500 if DB fails)
    # But since relation check is first, it should be 404 "Link lost"
    assert response.status_code == 404
    assert "Link lost" in response.json()["message"]


@pytest.mark.asyncio
async def test_chat_empty_message(client: AsyncClient):
    """Test Validation: Empty message should fail."""
    
    # Mock Auth
    from backend.app.api.dependencies import get_current_user
    from backend.app.main import app
    app.dependency_overrides[get_current_user] = lambda: User(user_id=TEST_USER_ID, account_tier="free")

    payload = {
        "soul_id": TEST_SOUL_ID,
        "message": "" # Empty
    }
    
    response = await client.post("/api/v1/chat/send", json=payload)
    
    assert response.status_code == 422 # Validation Error
