# /backend/tests/conftest.py
# v1.5.5 - Test Configuration (Fixed for pytest-asyncio)

import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from backend.app.core.config import settings
from backend.app.models import *  # Import all models for schema creation
# from backend.app.models.time_slot import TimeSlot # Removed redundant/incorrect import if covered by __init__

from backend.app.main import app
from backend.app.database.session import get_async_session
from backend.app.api.dependencies import get_current_user
from backend.app.models.user import User

# Use in-memory SQLite with shared cache for concurrency
TEST_DB_URL = "sqlite+aiosqlite:///file:memdb1?mode=memory&cache=shared"
from sqlalchemy.pool import NullPool

engine = create_async_engine(
    TEST_DB_URL, 
    connect_args={"check_same_thread": False}, 
    poolclass=NullPool
)

TestingSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# ✅ FIX: Let pytest-asyncio handle event loops automatically
# We do NOT define an event_loop fixture here anymore

@pytest.fixture(scope="function")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates a fresh database session for each test function.
    """
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session
    
    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

async def get_test_db():
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Creates a Test Client with database override.
    """
    app.dependency_overrides[get_async_session] = get_test_db
    
    # Use LIFESPAN context to ensure app startup/shutdown events fire
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def mock_auth():
    """Mocks the current user dependency to return a default architect user."""
    user = User(
        user_id="architect_001",
        username="TestArchitect",
        account_tier="architect"
    )
    # Define the mock dependency function
    async def get_mock_user():
        return user
        
    app.dependency_overrides[get_current_user] = get_mock_user
    yield user
    # Cleanup is handled by the client fixture's clear() or we can do it explicitly
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
