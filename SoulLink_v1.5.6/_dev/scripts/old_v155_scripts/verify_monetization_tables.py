import asyncio
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Load env explicitly
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend/.env"))
print(f"📂 Loading .env from: {env_path}")
load_dotenv(env_path)

from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

DATABASE_URL = os.getenv("SUPABASE_DB_URL")

async def verify_tables():
    if not DATABASE_URL:
        print("❌ ERROR: SUPABASE_DB_URL not found in environment!")
        return

    # 🔧 TRANSFORMATION LOGIC (Matching session.py)
    async_url = DATABASE_URL
    
    # 1. Strip sslmode (asyncpg doesn't like it in URL)
    if "sslmode=" in async_url:
        u = urlparse(async_url)
        q = parse_qs(u.query)
        q.pop('sslmode', None)
        async_url = urlunparse(u._replace(query=urlencode(q, doseq=True)))
    
    # 2. Update protocol
    if async_url.startswith("postgresql://"):
        async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")
        
    print(f"🔌 Connecting to DB (Protocol adjusted)...")
    
    try:
        engine = create_async_engine(async_url)
        async with engine.connect() as conn:
            print("🔍 Checking 'user_soul_state' table...")
            try:
                result = await conn.execute(text("SELECT count(*) FROM user_soul_state"))
                count = result.scalar()
                print(f"✅ Table 'user_soul_state' EXISTS! Row count: {count}")
                
            except Exception as e:
                print(f"❌ ERROR: 'user_soul_state' table check failed: {e}")

            print("🔍 Checking 'ad_impressions' table...")
            try:
                result = await conn.execute(text("SELECT count(*) FROM ad_impressions"))
                count = result.scalar()
                print(f"✅ Table 'ad_impressions' EXISTS! Row count: {count}")
            except Exception as e:
                print(f"❌ ERROR: 'ad_impressions' table check failed: {e}")
                
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(verify_tables())
