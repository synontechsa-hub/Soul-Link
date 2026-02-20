import asyncio
from backend.app.database.session import async_session_maker
from sqlalchemy import text

async def fix_db():
    async with async_session_maker() as session:
        print("🔍 Checking schema...")
        
        # 1. Add total_messages_sent to link_states
        try:
            await session.execute(text("ALTER TABLE link_states ADD COLUMN total_messages_sent INTEGER DEFAULT 0"))
            print("✅ Added total_messages_sent to link_states")
        except Exception as e:
            if "already exists" in str(e).lower():
                print("ℹ️ total_messages_sent already exists")
            else:
                print(f"❌ Failed to add total_messages_sent: {e}")

        # 2. Fix conversations.msg_id
        # Check if msg_id exists
        res = await session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'conversations'"))
        columns = [r[0] for r in res.fetchall()]
        print(f"Current columns in conversations: {columns}")
        
        if "msg_id" not in columns:
            if "id" in columns:
                try:
                    await session.execute(text("ALTER TABLE conversations RENAME COLUMN id TO msg_id"))
                    print("✅ Renamed conversations.id to msg_id")
                except Exception as e:
                    print(f"❌ Failed to rename id: {e}")
            else:
                try:
                    await session.execute(text("ALTER TABLE conversations ADD COLUMN msg_id VARCHAR(36) PRIMARY KEY"))
                    print("✅ Added msg_id to conversations")
                except Exception as e:
                    print(f"❌ Failed to add msg_id: {e}")
        else:
            print("ℹ️ conversations.msg_id already exists")

        await session.commit()
        print("🚀 Database migration check complete.")

if __name__ == "__main__":
    asyncio.run(fix_db())
