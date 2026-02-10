📋 SoulLink v1.5.5 - Technical Audit & Performance Report
Date: 2026-02-09 Status: 🔴 CRITICAL PERFORMANCE ISSUES DETECTED Target: Backend Optimization

🚨 1. The "Heavy Pillar" Drag (Database/Memory)
Severity: Critical Location: backend/app/services/location_resolver.py & backend/app/models/soul.py

❌ The Issue
The logs show a query taking 1.34s to fetch just 17 rows.

SELECT ... FROM soul_pillars

Your SoulPillar model contains massive text columns: interaction_engine (LLM prompts/fine-tuning data), personality, and background. In LocationResolver.resolve_bulk_locations, you are likely running a standard select(SoulPillar). This fetches all columns. You are dragging megabytes of text from the DB into Python memory just to check a timestamp in the routines JSON.

✅ The Fix
Lazy Load Columns: Update the query in LocationResolver to fetch only what is needed for location logic.

Python

# In backend/app/services/location_resolver.py

stmt = select(SoulPillar).options(
    load_only(SoulPillar.soul_id, SoulPillar.routines)
)
🔁 2. Redundant Cache Warming (The Loop of Death)
Severity: Critical Location: backend/app/logic/time_manager.py -> warm_world_state_cache

❌ The Issue
The logs show the heavy soul_pillars query running repeatedly:

✅ Cached morning -> SELECT... -> ✅ Cached afternoon -> SELECT...

Your warm_world_state_cache function iterates through TimeSlot enum. Inside that loop, it calls resolve_bulk_locations. Because of Issue #1, you are re-fetching those massive heavy objects 5 times (Morning, Afternoon, Evening, Night, Late Night) in a row.

✅ The Fix
Hoist the Fetch: Fetch the SoulPillar data once into memory before the loop starts. Pass this lightweight list of routines to the resolver.

🛑 3. Blocking I/O on Startup (Server Freeze)
Severity: High Location: backend/app/services/backup_service.py

❌ The Issue
[INFO] [System.Backup] ... Saved 17 souls (Happens during startup sequence)

Your System.Backup runs on boot. Inside backup_service.py, you are likely using standard open() and json.dump():

Python
with open(filename, 'w') as f: # This blocks the entire async event loop!
    json.dump(data, f)
While this writes to disk, nothing else can happen. No health checks, no DB connections, no requests. As the DB grows, your startup time will degrade linearly.

✅ The Fix
Run in Executor: Offload file I/O to a separate thread so the main loop keeps running.

Python
import aiofiles

# OR

loop = asyncio.get_running_loop()
await loop.run_in_executor(None, write_sync_backup_function, data)
🐢 4. The "One User" Lag (0.7s Latency)
Severity: High Location: backend/app/api/users.py or dependencies.py

❌ The Issue
[WARNING] ... SLOW QUERY (0.7007s): SELECT users.user_id... FROM users

It took 0.7 seconds to fetch 1 user. This suggests your users table has a column that is unexpectedly large (e.g., are you storing base64 profile images directly in bio or meta_data?) or the DB connection latency is massive.

✅ The Fix
Check the users table schema size.

Ensure you have an index on user_id (likely yes, as it's PK).

If columns are large, use defer() to skip loading them on standard authentication checks.

🚧 5. Rate Limiting Configuration (Proxy Issue)
Severity: Medium Location: backend/app/core/rate_limiter.py

❌ The Issue
You are using get_remote_address:

Python
limiter = Limiter(key_func=get_remote_address)
If you deploy this via Docker, Nginx, or a Cloud Load Balancer, get_remote_address often sees the Gateway IP (e.g., 172.18.0.1) instead of the user's real IP. Result: If one user spams, the rate limiter bans the Gateway IP, blocking all users.

✅ The Fix
Configure slowapi to trust X-Forwarded-For headers if running behind a proxy.

📦 6. Strict Payload Limits
Severity: Medium Location: backend/app/middleware/request_size_limit.py

❌ The Issue
Middleware stack initialized: Performance, Size Limit (1MB)

1MB is very small if you plan to allow:

High-res avatar uploads.

Voice messages (audio files).

Rich text logs with embedded metadata.

✅ The Fix
Increase the limit to 5MB or 10MB in backend/app/main.py.
