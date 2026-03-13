
import asyncio
from datetime import timedelta
from backend.app.database.session import async_session_maker
from backend.app.models.user import User
from backend.app.core.utils import utcnow

async def trigger_time_jump():
    async with async_session_maker() as session:
        user_uuid = "14dd612d-744e-487d-b2d5-cc47732183d3"
        user = await session.get(User, user_uuid)
        if user:
            # Set last_seen_at to 5 hours ago
            user.last_seen_at = utcnow() - timedelta(hours=5)
            session.add(user)
            await session.commit()
            print(f"Updated user {user.username} last_seen_at to 5 hours ago.")
        else:
            print("User not found.")

if __name__ == "__main__":
    asyncio.run(trigger_time_jump())
