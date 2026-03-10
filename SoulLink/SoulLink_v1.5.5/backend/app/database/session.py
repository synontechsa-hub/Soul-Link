# /backend/app/database/session.py
# /version.py
# /_dev/

# "I am the box. I am the logic."
# - GLaDOS - Portal

from sqlmodel import Session, create_engine
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger
import time
from sqlalchemy import event, Engine

logger = get_logger("Database")

# ⚡ QUERY PERFORMANCE MONITORING
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    # Check if start time was set (might be missing in some test contexts)
    if hasattr(context, '_query_start_time'):
        total = time.time() - context._query_start_time
        if total > 0.5:  # Log queries slower than 500ms
            logger.warning(f"SLOW QUERY ({total:.4f}s): {statement}")

# 🔌 The Sync Engine (Legacy/Scripts)
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Check if we are using Supabase Transaction Pooler (Port 6543)
# For Transaction Mode, we must disable SQLAlchemy pooling to avoid conflicts.
engine_args = {
    "echo": False,
    "connect_args": connect_args
}

if ":6543" in settings.database_url:
    engine_args["poolclass"] = NullPool
else:
    # ⚡ STABILITY: Connection Pooling
    # Keep a pool of connections ready to avoid handshake overhead
    engine_args["pool_pre_ping"] = True
    engine_args["pool_size"] = 20        # Baseline connections
    engine_args["max_overflow"] = 10     # Burst capacity
    engine_args["pool_timeout"] = 30     # Max wait for connection
    engine_args["pool_recycle"] = 1800   # Recycle every 30 mins

engine = create_engine(
    settings.database_url, 
    **engine_args
)

# ⚡ The Async Engine (Production/FastAPI)
async_url = settings.database_url

# Sanitization: asyncpg doesn't like 'sslmode' in the connection string
if "sslmode=" in async_url:
    from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
    u = urlparse(async_url)
    q = parse_qs(u.query)
    q.pop('sslmode', None)
    async_url = urlunparse(u._replace(query=urlencode(q, doseq=True)))

if async_url.startswith("postgresql://"):
    async_url = async_url.replace("postgresql://", "postgresql+asyncpg://")
elif async_url.startswith("sqlite:///"):
    async_url = async_url.replace("sqlite:///", "sqlite+aiosqlite:///")

# Async engine also benefits from NullPool in transaction mode
async_engine_args = {
    "echo": False,
}

# 🔧 PGBOUNCER FIX: Disable prepared statement cache
# Supabase uses pgbouncer in transaction mode, which doesn't support prepared statements
async_connect_args = {}
if async_url.startswith("postgresql+asyncpg://"):
    async_connect_args["statement_cache_size"] = 0

async_engine_args["connect_args"] = async_connect_args

if ":6543" in settings.database_url:
    async_engine_args["poolclass"] = NullPool
else:
    # ⚡ ASYNC POOLING
    async_engine_args["pool_pre_ping"] = True
    async_engine_args["pool_size"] = 20
    async_engine_args["max_overflow"] = 10
    async_engine_args["pool_timeout"] = 30
    async_engine_args["pool_recycle"] = 1800

async_engine = create_async_engine(async_url, **async_engine_args)

async_session_maker = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

def get_session():
    """Sync session for legacy scripts/tasks."""
    with Session(engine) as session:
        yield session

async def get_async_session():
    """Primary Async session for FastAPI endpoints."""
    async with async_session_maker() as session:
        yield session