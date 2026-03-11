import asyncio
from backend.app.database.session import async_session_maker
from backend.app.models.user import User

async def main():
    async with async_session_maker() as session:
        user = await session.get(User, "14dd612d-744e-487d-b2d5-cc47732183d3")
        if not user:
            print("User not found.")
            return
        
        print("User loaded:", user.user_id)
        
        print("Rolling back session...")
        await session.rollback()
        
        print("Accessing user_id...")
        try:
            print(user.user_id)
            print("Access SUCCESS")
        except Exception as e:
            print("ERROR:", type(e).__name__, str(e))

if __name__ == "__main__":
    asyncio.run(main())
