# /backend/app/api/ads.py
# v1.5.5 Monetization Framework

from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import hmac
import hashlib

from backend.app.database.session import get_async_session
from backend.app.models.user_soul_state import UserSoulState
from backend.app.models.ad_impression import AdImpression
from backend.app.models.user import User
from backend.app.core.config import settings
from backend.app.api.dependencies import get_current_user
import logging

logger = logging.getLogger("SoulLink.Ads")

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
    session: AsyncSession = Depends(get_async_session)
):
    """
    Server-Side Verification (SSV) endpoint for AppLovin.
    Validates the reward and updates user state.
    
    For now, uses mock validation. In production, this will verify
    HMAC signatures from AppLovin.
    """
    logger.info(f"SSV Callback: {payload.user_id} - {payload.reward_type}")
    
    # MOCK VALIDATION (replace with real HMAC check when you have SSV secret)
    is_valid = True
    if settings.applovin_ssv_secret != "mock_secret" and payload.signature:
        # Real validation
        expected_signature = hmac.new(
            settings.applovin_ssv_secret.encode(),
            f"{payload.user_id}{payload.reward_type}{payload.timestamp}".encode(),
            hashlib.sha256
        ).hexdigest()
        is_valid = hmac.compare_digest(expected_signature, payload.signature)
    
    if not is_valid:
        logger.warning(f"Invalid SSV signature for user {payload.user_id}")
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Get or create user_soul_state (for now, apply to all souls)
    # In production, you'd specify which soul this applies to
    result = await session.execute(
        select(UserSoulState).where(UserSoulState.user_id == payload.user_id)
    )
    states = result.scalars().all()
    
    if not states:
        logger.warning(f"No soul states found for user {payload.user_id}")
        # Create a default state for the user's first linked soul
        # This is a fallback; normally states are created when linking souls
    
    # Update stability for all souls (or specific soul if provided)
    for state in states:
        if payload.reward_type == "stability_boost":
            state.signal_stability = 100.0
            state.total_stability_boosts += 1
            state.updated_at = datetime.utcnow()
    
    # Log the ad impression
    impression = AdImpression(
        user_id=payload.user_id,
        ad_network=payload.ad_network,
        ad_type="rewarded",
        placement="stability_boost",  # or from payload
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
        "new_stability": 100.0,
        "message": "Signal restored!"
    }


@router.get("/user/stability", response_model=StabilityResponse)
async def get_user_stability(
    soul_id: Optional[str] = None,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Get current signal stability for a user-soul pair.
    If no soul_id provided, returns average across all souls.
    """
    query = select(UserSoulState).where(UserSoulState.user_id == user.user_id)
    
    if soul_id:
        query = query.where(UserSoulState.soul_id == soul_id)
    
    result = await session.execute(query)
    states = result.scalars().all()
    
    if not states:
        # No state yet, return default
        return StabilityResponse(
            signal_stability=100.0,
            decay_rate=settings.ad_stability_decay_rate,
            warning_threshold=settings.ad_stability_warning_threshold,
            last_updated=datetime.utcnow()
        )
    
    # Return first state (or average if multiple)
    state = states[0]
    
    return StabilityResponse(
        signal_stability=state.signal_stability,
        decay_rate=settings.ad_stability_decay_rate,
        warning_threshold=settings.ad_stability_warning_threshold,
        last_updated=state.updated_at
    )


@router.post("/user/nsfw-toggle")
async def toggle_nsfw(
    payload: NSFWToggleRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Toggle NSFW mode for a specific soul.
    When enabled, ads are disabled for that soul's chat.
    """
    # Get or create user_soul_state
    result = await session.execute(
        select(UserSoulState).where(
            UserSoulState.user_id == user.user_id,
            UserSoulState.soul_id == payload.soul_id
        )
    )
    state = result.scalar_one_or_none()
    
    if not state:
        # Create new state
        state = UserSoulState(
            user_id=user.user_id,
            soul_id=payload.soul_id,
            nsfw_enabled=payload.nsfw_enabled
        )
        session.add(state)
    else:
        state.nsfw_enabled = payload.nsfw_enabled
        state.updated_at = datetime.utcnow()
    
    await session.commit()
    
    logger.info(f"NSFW toggled for {user.user_id}/{payload.soul_id}: {payload.nsfw_enabled}")
    
    return {
        "success": True,
        "ads_disabled_for_soul": payload.nsfw_enabled
    }
