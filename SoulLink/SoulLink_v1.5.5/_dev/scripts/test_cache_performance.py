
import asyncio
import time
import sys
from pathlib import Path
from httpx import AsyncClient

# Setup project path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.main import app
from httpx import ASGITransport

async def benchmark_endpoint(url: str, name: str):
    print(f"--- Benchmarking {name} ({url}) ---")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. First Call (Miss)
        start = time.perf_counter()
        await client.get(url)
        miss_time = (time.perf_counter() - start) * 1000
        print(f"   [MISS] Time: {miss_time:.2f}ms")

        # 2. Second Call (Hit)
        start = time.perf_counter()
        await client.get(url)
        hit_time = (time.perf_counter() - start) * 1000
        print(f"   [HIT ] Time: {hit_time:.2f}ms")
        
        speedup = ((miss_time - hit_time) / miss_time) * 100
        print(f"   Result: ~{speedup:.1f}% faster")

async def main():
    import traceback
    try:
        print("LOG: CACHE PERFORMANCE AUDIT\n" + "="*30)
        
        from backend.app.api.dependencies import get_current_user
        from backend.app.models.user import User
        from backend.app.database.session import engine
        from sqlmodel import Session, select
        
        # 0. Provision the user in DB for the benchmark to find
        test_uid = "bench-user-123"
        try:
            with Session(engine) as session:
                stmt = select(User).where(User.user_id == test_uid)
                existing = session.exec(stmt).first()
                if not existing:
                    u = User(
                        user_id=test_uid, 
                        username="bench", 
                        display_name="Benchmarking User",
                        account_tier="Basic",
                        gems=100,
                        energy=50,
                        current_location="soul_plaza",
                        current_time_slot="morning"
                    )
                    session.add(u)
                    session.commit()
                    print(f"   [INIT] Created test user: {test_uid}")
        except Exception as e:
            # Likely already exists or session conflict, safe to ignore for benchmark
            pass
        
        # Mocking the dependency for the duration of this script
        app.dependency_overrides[get_current_user] = lambda: User(
            user_id=test_uid, 
            username="bench", 
            account_tier="Basic",
            gems=100,
            energy=50,
            current_location="soul_plaza",
            current_time_slot="morning"
        )

        await benchmark_endpoint("/api/v1/users/me", "User Profile")
        await benchmark_endpoint("/api/v1/map/locations", "World Map")
        
        app.dependency_overrides.clear()
    except Exception:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
