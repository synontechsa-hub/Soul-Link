
import asyncio
from sqlmodel import select
from backend.app.database.session import async_session_maker
from backend.app.models.soul import Soul

async def list_souls():
    async with async_session_maker() as session:
        res = await session.execute(select(Soul).limit(1))
        soul = res.scalars().first()
        if soul:
            print(soul.soul_id)
        else:
            print("No souls found.")

if __name__ == "__main__":
    asyncio.run(list_souls())
