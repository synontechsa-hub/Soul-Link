# /backend/app/api/dependencies.py
# v1.5.6 Normandy SR-2
# UPDATED: Removed debug prints, wrapped blocking Supabase call, added UUID cache.

"""
Authentication & User Management Dependencies
Integrates Supabase Auth for secure JWT validation and Architect Role checks.
"""

import asyncio
import hashlib
from datetime import datetime, timezone, timedelta
from fastapi import Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database.session import get_async_session
from backend.app.models.user import User
from backend.app.core.config import settings
from backend.app.core.logging_config import get_logger
from backend.app.core.cache import cache_service
from typing import Optional
from supabase import create_client, Client

logger = get_logger("Dependencies")

# ⚡ SUPABASE CLIENT SINGLETON
# Initialize once, reuse everywhere
supabase: Optional[Client] = None
try:
    if settings.supabase_url and settings.supabase_anon_key and "sb_publishable" not in settings.supabase_anon_key:
        supabase = create_client(settings.supabase_url, settings.supabase_anon_key)
        logger.info(f"✅ Supabase Client Init: {settings.supabase_url[:20]}...")
    elif settings.environment == "development":
        logger.warning("⚠️ Running without Supabase (Local Dev Mode active)")
    else:
        logger.critical("❌ CRITICAL: Invalid Supabase keys in production!")
        raise RuntimeError("Cannot start production server without Supabase connection")
except Exception as e:
    if settings.environment == "development":
        logger.warning(f"⚠️ Supabase Init Failed (Local Dev Mode active): {e}")
    else:
        logger.critical(f"❌ CRITICAL: Supabase Init Failed: {e}")
        raise RuntimeError("Cannot start server without Supabase connection") from e

security = HTTPBearer()

# Cache TTL for validated user UUIDs (seconds)
# Avoids hitting Supabase on every single request.
_UUID_CACHE_TTL = 60


def _validate_token_sync(token: str) -> Optional[str]:
    """
    Synchronous Supabase token validation.
    Runs in a thread pool via run_in_executor to avoid blocking the async event loop.
    Returns user_id on success, None on failure.
    """
    # [DEV BYPASS] Local dev mock token support
    if settings.environment == "development" and token == "dev_mock_token_123":
        return settings.architect_uuid or "14dd612d-744e-487d-b2d5-cc47732183d3"
        
    if not supabase:
        return None
        
    try:
        user_response = supabase.auth.get_user(token)
        if user_response and user_response.user:
            return user_response.user.id
        return None
    except Exception as e:
        logger.debug(f"Token validation error: {type(e).__name__}")
        return None


async def get_current_user_uuid(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Validates Supabase JWT and returns the user UUID.
    - Checks a short-lived cache first (60s TTL) to avoid Supabase round-trips.
    - Runs the blocking Supabase call in a thread pool executor.
    """
    token = credentials.credentials

    # [DEV BYPASS] Allow mock token if Supabase is offline
    if not supabase and not (settings.environment == "development" and token == "dev_mock_token_123"):
        raise HTTPException(500, detail="Auth Server Unavailable")

    # Normandy-SR2 Fix: Secure cache key using SHA256 to avoid collisions
    token_hash = hashlib.sha256(token.encode()).hexdigest()[:32]
    cache_key = f"auth:uuid:{token_hash}"

    cached_uuid = cache_service.get(cache_key)
    if cached_uuid:
        return cached_uuid

    # Normandy-SR2 Fix: Use get_running_loop (Python 3.10+)
    loop = asyncio.get_running_loop()
    user_id = await loop.run_in_executor(None, _validate_token_sync, token)

    if not user_id:
        raise HTTPException(401, detail="Invalid or Expired Token")

    # Cache the validated UUID
    cache_service.set(cache_key, user_id, ttl=_UUID_CACHE_TTL)

    return user_id


async def get_current_user(
    user_uuid: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Fetches the local User record asynchronously.
    If the user exists in Supabase but not locally, JIT creates them.
    """
    user = await session.get(User, user_uuid)

    if not user:
        # JIT Provisioning
        new_user = User(
            user_id=user_uuid,
            username=f"Guest-{user_uuid[:8]}",
            account_tier="free"
        )
        session.add(new_user)
        try:
            await session.commit()
            await session.refresh(new_user)
        except Exception as e:
            await session.rollback()
            logger.error(
                f"Failed to create user {user_uuid}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail="Failed to create user account")
        return new_user

    # Chronicle Heartbeat: update last_seen_at if stale (>5 min) to power
    # the narrator time-jump system without a DB write on every single request.
    now = datetime.now(timezone.utc)
    if user.last_seen_at is None or (now - user.last_seen_at) > timedelta(minutes=5):
        user.last_seen_at = now
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
        except Exception as e:
            await session.rollback()  # Non-fatal — don't block the request
            logger.error(f"Heartbeat update failed for user {user_uuid}: {e}", exc_info=True)
            # Re-fetch user to clear the rolled-back/expired state
            user = await session.get(User, user_uuid)
            assert user is not None, "User vanished after rollback"

    return user


def _check_architect_role_sync(token: str) -> Optional[str]:
    """
    Synchronous architect role check.
    Runs in thread pool via run_in_executor.
    """
    # [DEV BYPASS] Local dev mock token support
    if settings.environment == "development" and token == "dev_mock_token_123":
        return settings.architect_uuid or "14dd612d-744e-487d-b2d5-cc47732183d3"
        
    if not supabase:
        return None
        
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response or not user_response.user:
            return None
        roles = user_response.user.app_metadata.get("role", "")
        if "architect" not in roles and roles != "architect":
            return None
        return user_response.user.id
    except Exception as e:
        logger.debug(f"Architect role check error: {type(e).__name__}")
        return None


async def require_architect_role(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Checks if the user has the 'architect' role.
    Normandy-SR2 Refinement: Hardcoded fallback for the primary Architect UUID.
    """
    token = credentials.credentials

    if not supabase:
        raise HTTPException(500, detail="Auth Server Unavailable")

    # Secure cache check
    token_hash = hashlib.sha256(token.encode()).hexdigest()[:32]
    cache_key = f"auth:architect:{token_hash}"
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    loop = asyncio.get_running_loop()
    user_id = await loop.run_in_executor(None, _check_architect_role_sync, token)

    # Dynamic God-Mode Fallback from Environment (Architect Dev Account)
    if settings.architect_uuid and user_id == settings.architect_uuid:
        logger.info(f"👑 Global Architect Identified: {user_id}")
    elif not user_id:
        raise HTTPException(status_code=403, detail="⛔ ARCHITECT ACCESS ONLY")

    if user_id is None:
        raise HTTPException(status_code=403, detail="⛔ ARCHITECT ACCESS ONLY")

    cache_service.set(cache_key, user_id, ttl=_UUID_CACHE_TTL)
    return user_id


# Dependency aliases
CurrentUserId = Depends(get_current_user_uuid)
CurrentUser = Depends(get_current_user)
ArchitectOnly = Depends(require_architect_role)
