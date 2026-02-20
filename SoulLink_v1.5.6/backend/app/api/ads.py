# /backend/app/api/ads.py
# v1.5.6 Monetization Framework
# UPDATED: Now uses LinkState instead of UserSoulState (consolidated mirror system)

from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import hmac
import hashlib

from backend.app.database.session import get_async_session
from backend.app.models.link_state import LinkState
from backend.app.models.ad_impression import AdImpression
from backend.app.models.user import User
from backend.app.core.config import settings
from backend.app.core.cache import cache_service
from backend.app.api.dependencies import get_current_user
from backend.app.core.rate_limiter import limiter, RateLimits
from backend.app.core.logging_config import get_logger

logger = get_logger("SoulLink.Ads")

router = APIRouter(tags=["ads"])


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class AdConfigResponse(BaseModel):
    """Ad configuration served to frontend"""
    applovin_sdk_key: str
    tapjoy_sdk_key: str
    tapjoy_app_id: str
    stability_decay_rate: float
    stability_warning_threshold: float
    ad_cooldown_seconds: int


class SSVRewardRequest(BaseModel):
    """Server-Side Verification callback from AppLovin"""
    user_id: str
    soul_id: Optional[str] = None  # Which soul's link to restore (optional: restores all if omitted)
    reward_type: str  # 'stability_boost', 'energy', 'city_credits'
    ad_network: str = "applovin"
    signature: Optional[str] = None
    timestamp: Optional[str] = None


class StabilityResponse(BaseModel):
    """Current stability status"""
    signal_stability: float
    decay_rate: float
    warning_threshold: float
    last_updated: datetime


class NSFWToggleRequest(BaseModel):
    """Toggle NSFW for a specific soul"""
    soul_id: str
    nsfw_enabled: bool


# ==========================================
# ENDPOINTS
# ==========================================

@router.get("/ads/config", response_model=AdConfigResponse)
async def get_ad_config(
    user: User = Depends(get_current_user)
):
    """
    Serve ad network configuration to frontend.
    This keeps SDK keys out of the APK/source code.
    """
    return AdConfigResponse(
        applovin_sdk_key=settings.applovin_sdk_key,
        tapjoy_sdk_key=settings.tapjoy_sdk_key,
        tapjoy_app_id=settings.tapjoy_app_id,
        stability_decay_rate=settings.ad_stability_decay_rate,
        stability_warning_threshold=settings.ad_stability_warning_threshold,
        ad_cooldown_seconds=settings.ad_cooldown_seconds
    )


@router.post("/ads/verify-reward")
async def verify_ad_reward(
    payload: SSVRewardRequest,
    user: User = Depends(get_current_user), # Normandy-SR2 Fix: Enforcement
    session: AsyncSession = Depends(get_async_session)
):
    """
    Server-Side Verification (SSV) endpoint for AppLovin.
    Validates the reward and updates the user's LinkState(s).
    """
    # Normandy-SR2 Fix: Ensure the user being rewarded is the one who watched the ad
    if payload.user_id != user.user_id:
        logger.warning(f"Spoofing attempt detected: {user.user_id} tried to claim reward for {payload.user_id}")
        raise HTTPException(status_code=403, detail="Reward identity mismatch.")

    logger.info(f"SSV Callback: user={payload.user_id} soul={payload.soul_id} type={payload.reward_type}")

    # --- SIGNATURE VALIDATION ---
    is_valid = True
    if settings.applovin_ssv_secret != "mock_secret" and payload.signature:
        expected_signature = hmac.new(
            settings.applovin_ssv_secret.encode(),
            f"{payload.user_id}{payload.reward_type}{payload.timestamp}".encode(),
            hashlib.sha256
        ).hexdigest()
        is_valid = hmac.compare_digest(expected_signature, payload.signature)

    if not is_valid:
        logger.warning(f"Invalid SSV signature for user {payload.user_id}")
        raise HTTPException(status_code=403, detail="Invalid signature")

    # --- FETCH LINK STATE(S) ---
    query = select(LinkState).where(LinkState.user_id == payload.user_id)
    if payload.soul_id:
        # Restore a specific soul's link
        query = query.where(LinkState.soul_id == payload.soul_id)

    result = await session.execute(query)
    links = result.scalars().all()

    if not links:
        logger.warning(f"No LinkState found for user {payload.user_id} (soul={payload.soul_id})")
        raise HTTPException(status_code=404, detail="No active soul link found for this user.")

    # --- APPLY REWARD ---
    new_stability = 100.0
    for link in links:
        if payload.reward_type == "stability_boost":
            link.signal_stability = new_stability
            link.last_stability_decay = datetime.utcnow()
            session.add(link)

            # Invalidate stability cache
            cache_service.delete(f"link:stability:{link.user_id}:{link.soul_id}")

    # --- LOG IMPRESSION ---
    impression = AdImpression(
        user_id=payload.user_id,
        ad_network=payload.ad_network,
        ad_type="rewarded",
        placement="stability_boost",
        reward_granted=True,
        reward_type=payload.reward_type,
        reward_amount=100.0 if payload.reward_type == "stability_boost" else None,
        ssv_verified=True,
        ssv_signature=payload.signature
    )
    session.add(impression)

    await session.commit()

    logger.info(f"✅ Reward granted: {payload.reward_type} to {payload.user_id}")

    return {
        "success": True,
        "new_stability": new_stability,
        "links_restored": len(links),
        "message": "Signal restored!"
    }


@router.get("/user/stability", response_model=StabilityResponse)
@limiter.limit(RateLimits.READ_ONLY)
async def get_user_stability(
    request: Request,
    soul_id: Optional[str] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get current signal stability for a user-soul pair from LinkState.
    If no soul_id provided, returns the lowest stability across all links (worst-case).
    """
    # Check cache first
    cache_key = f"link:stability:{user.user_id}:{soul_id or 'all'}"
    cached = cache_service.get(cache_key)
    if cached:
        return StabilityResponse(**cached)

    query = select(LinkState).where(LinkState.user_id == user.user_id)
    if soul_id:
        query = query.where(LinkState.soul_id == soul_id)

    result = await session.execute(query)
    links = result.scalars().all()

    if not links:
        # No links yet — return default healthy state
        return StabilityResponse(
            signal_stability=100.0,
            decay_rate=settings.ad_stability_decay_rate,
            warning_threshold=settings.ad_stability_warning_threshold,
            last_updated=datetime.utcnow()
        )

    # Return the worst stability (most urgent for the user to know about)
    weakest_link = min(links, key=lambda l: l.signal_stability)

    response_data = {
        "signal_stability": weakest_link.signal_stability,
        "decay_rate": settings.ad_stability_decay_rate,
        "warning_threshold": settings.ad_stability_warning_threshold,
        "last_updated": weakest_link.last_stability_decay.isoformat()
    }
    cache_service.set(cache_key, response_data, ttl=300)  # 5 min cache

    return StabilityResponse(
        signal_stability=weakest_link.signal_stability,
        decay_rate=settings.ad_stability_decay_rate,
        warning_threshold=settings.ad_stability_warning_threshold,
        last_updated=weakest_link.last_stability_decay
    )


@router.post("/user/nsfw-toggle")
@limiter.limit(RateLimits.USER_WRITE)
async def toggle_nsfw(
    payload: NSFWToggleRequest,
    request: Request,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Toggle NSFW mode for a specific soul via LinkState.
    """
    result = await session.execute(
        select(LinkState).where(
            LinkState.user_id == user.user_id,
            LinkState.soul_id == payload.soul_id
        )
    )
    link = result.scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=404,
            detail=f"No active link with soul '{payload.soul_id}'. Link with this soul first."
        )

    link.unlocked_nsfw = payload.nsfw_enabled
    session.add(link)
    await session.commit()

    logger.info(f"NSFW toggled for {user.user_id}/{payload.soul_id}: {payload.nsfw_enabled}")

    return {
        "success": True,
        "soul_id": payload.soul_id,
        "nsfw_enabled": link.unlocked_nsfw
    }
