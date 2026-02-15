import asyncio
import sys
from pathlib import Path
from sqlalchemy import text

# Path setup to import backend modules
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.database.session import async_engine

async def fix_schema():
    print("🔧 Starting Async Schema Repair...")
    
    try:
        async with async_engine.begin() as conn:
            print("Checking locations table...")
            # Use safe "ADD COLUMN IF NOT EXISTS" if Postgres supports it (Postgres 9.6+)
            # Supabase (Postgres 15+) supports it.
            await conn.execute(text("ALTER TABLE locations ADD COLUMN IF NOT EXISTS image_url VARCHAR(255)"))
            print("✅ Schema Repair Command Executed.")
            
    except Exception as e:
        print(f"❌ Schema Repair Failed: {e}")
    finally:
        await async_engine.dispose()

if __name__ == "__main__":
    # Windows SelectorEventLoop policy fix for asyncio
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(fix_schema())
