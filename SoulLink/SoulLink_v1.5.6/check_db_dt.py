
import asyncio
from sqlmodel import select
from backend.app.database.session import async_session_maker
from backend.app.models.user import User
from backend.app.core.config import settings

async def check_user_datetime():
    async with async_session_maker() as session:
        # Use the architect UUID which is what dev_mock_token_123 returns
        user_uuid = "14dd612d-744e-487d-b2d5-cc47732183d3"
        user = await session.get(User, user_uuid)
        if user:
            print(f"User: {user.username}")
            print(f"last_seen_at: {user.last_seen_at}")
            print(f"tzinfo: {user.last_seen_at.tzinfo if user.last_seen_at else 'None'}")
        else:
            print("User not found.")

if __name__ == "__main__":
    asyncio.run(check_user_datetime())
