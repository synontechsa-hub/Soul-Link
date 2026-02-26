import asyncio
from backend.app.database.session import async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.api.map import get_location_narration


async def test():
    async with AsyncSession(async_engine) as session:
        user = await session.get(User, '14dd612d-744e-487d-b2d5-cc47732183d3')
        if not user:
            print('User not found')
            return

        try:
            res = await get_location_narration('soul_plaza', user, session)
            import json
            print(json.dumps(res, indent=2))
        except Exception as e:
            print('Error:', e)

asyncio.run(test())
