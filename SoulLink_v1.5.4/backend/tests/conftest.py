
import pytest
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator, Generator
from backend.app.main import app
from backend.app.api.dependencies import get_current_user
from backend.app.models.user import User

# Sanity check: Ensure we are in test environment (optional)
# os.environ["ENVIRONMENT"] = "testing"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="module")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture for async HTTP client bonded to the FastAPI app.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest.fixture(scope="function")
def mock_auth(client: AsyncClient):
    """
    Fixture to mock the authentication dependency.
    Application will believe a valid user is logged in.
    """
    mock_user = User(
        user_id="00000000-0000-0000-0000-000000000000",
        email="test@example.com", # Note: User model does not explicitly store email, but we pass it for completeness acting as if decoded from JWT
        username="TestArchitect",
        account_tier="architect",
        current_location="linkside_apartment",
        current_time_slot="morning",
        energy=100,
        gems=1000
    )
    
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield mock_user
    app.dependency_overrides = {}
