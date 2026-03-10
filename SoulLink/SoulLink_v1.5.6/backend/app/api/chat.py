# /backend/app/api/chat.py
# v1.5.6 Normandy SR-2 Chat API

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from backend.app.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.logic.brain import LegionBrain
from backend.app.models.user import User
# v1.5.6 New Models
from backend.app.models.link_state import LinkState
from backend.app.models.user_persona import UserPersona
from backend.app.models.conversation import Conversation
from backend.app.models.time_slot import TimeSlot
from backend.app.services.narrator import NarratorService
from backend.app.services.persona_service import PersonaService

from backend.app.api.dependencies import get_current_user
from backend.app.logic.time_manager import TimeManager
from backend.app.core.rate_limiter import limiter, RateLimits
from backend.app.core.validation import ValidatedChatRequest
from backend.app.core.logging_config import get_logger
from backend.app.core.config import settings
from pydantic import BaseModel
from typing import Optional
from datetime import datetime as dt

router = APIRouter(prefix="/chat", tags=["Legion Engine - Chat"])
logger = get_logger("ChatAPI")

# ⚡ UPDATED RESPONSE MODEL


class ChatResponse(BaseModel):
    soul_id: str
    response: str
    tier: str
    intimacy_score: int
    location: str
    is_architect: bool
    debug_info: Optional[dict] = None
    # <--- NEW: For Chronicle/Narrator events
    system_event: Optional[dict] = None


@router.post("/send", response_model=ChatResponse)
@limiter.limit(RateLimits.CHAT)
async def send_message(
    chat_request: ValidatedChatRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    logger.info(
        f"Chat request from user={user.user_id} to soul={chat_request.soul_id}")
    brain = LegionBrain(session)

    # 1. FETCH LINK STATE (The Mirror)
    # Replaces old Relationship + UserSoulState logic

    # Fast validation: does the soul even exist?
    from backend.app.models.soul import Soul
    soul_exists = await session.get(Soul, chat_request.soul_id)
    if not soul_exists:
        raise HTTPException(
            status_code=404, detail="Link lost. Soul not found.")

    link_result = await session.execute(
        select(LinkState).where(
            LinkState.user_id == user.user_id,
            LinkState.soul_id == chat_request.soul_id
        )
    )
    link = link_result.scalars().first()

    if not link:
        # Auto-create LinkState if missing
        is_architect = user.user_id == settings.architect_uuid

        # Get soul state for initial location
        from backend.app.models.soul import SoulState
        state = await session.get(SoulState, chat_request.soul_id)

        link = LinkState(
            user_id=user.user_id,
            soul_id=chat_request.soul_id,
            current_location=state.current_location_id if state else None,
            signal_stability=100.0,
            intimacy_tier="SOUL_LINKED" if is_architect else "STRANGER",
            is_architect=is_architect,
            unlocked_nsfw=is_architect
        )
        session.add(link)
        await session.flush()

    # 2. CHECK STABILITY & ENERGY
    if link.signal_stability <= 0:
        raise HTTPException(
            status_code=402, detail="Signal lost. Restore stability to continue.")

    # v1.5.6 Normandy-SR2 Fix: Energy System integration
    from backend.app.services.energy_system import EnergySystem
    is_fast_mode = await EnergySystem.check_and_deduct_energy(user, session)
    if not is_fast_mode:
        # In a real app, we'd handle slow-mode gating here. For now, we report it.
        logger.warning(
            f"User {user.user_id} is in SLOW MODE (Energy Depleted)")

    # 3. IDENTIFY PERSONA
    persona = await PersonaService.get_active_persona(session, user.user_id)
    if not persona:
        # Fallback: Create default from User Account
        persona = await PersonaService.create_default_persona(session, user)

    # 4. 🕰️ NARRATOR INTERVENTION (The Chronicle)
    narrator_event = None
    world_injection = ""

    # Use last_seen_at for time-jump if available (more accurate than link interaction)
    time_jump_anchor = user.last_seen_at or link.last_interaction

    if time_jump_anchor and NarratorService.check_time_jump(time_jump_anchor):
        # Resolve real weather for this user's world state
        from backend.app.services.weather_service import WeatherService
        weather_string = WeatherService.get_weather_string(
            calendar_day=user.calendar_day,
            calendar_month=user.calendar_month,
            calendar_year=user.calendar_year,
            current_season=user.current_season,
            current_weather=user.current_weather,
        )
        chronicle_text = await NarratorService.generate_chronicle(
            time_jump_anchor,
            link.current_location or "the city",
            weather_string
        )

        # Insert Chronicle Message into DB
        chronicle_msg = Conversation(
            user_id=user.user_id,
            soul_id=chat_request.soul_id,
            role="system",
            content=chronicle_text,
            meta_data={"flag": "chronicle"}
        )
        session.add(chronicle_msg)
        await session.flush()

        narrator_event = {
            "type": "chronicle_break",
            "text": chronicle_text
        }

        # Inject into prompt
        world_injection = f"[SYSTEM EVENT] {chronicle_text}"

        logger.info(
            f"Chronicle triggered for {user.user_id}: {chronicle_text}")

    # 5. GENERATE RESPONSE
    try:
        response_text = await brain.generate_response(
            user_id=user.user_id,
            soul_id=chat_request.soul_id,
            user_input=chat_request.message,
            session=session,
            link_state=link,     # <--- PASSING LINK
            persona=persona,     # <--- PASSING PERSONA
            world_state_injection=world_injection
        )

        # 6. RETURN (Stability decay moved into brain.py for atomic commit)
        return ChatResponse(
            soul_id=chat_request.soul_id,
            response=response_text,
            tier=link.intimacy_tier,
            intimacy_score=link.intimacy_score,
            location=link.current_location or "Unknown",
            is_architect=link.is_architect,
            system_event=narrator_event
        )

    except Exception as e:
        import traceback
        logger.error(f"Brain Error: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(
            status_code=500, detail=f"Neural Link Failure: {str(e)}")


@router.get("/history")
@limiter.limit(RateLimits.READ_ONLY)
async def get_chat_history(
    soul_id: str,
    limit: int = 50,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    request: Request = None,
):
    """Fetch conversation history for a user-soul pair."""
    result = await session.execute(
        select(Conversation)
        .where(
            Conversation.user_id == user.user_id,
            Conversation.soul_id == soul_id,
        )
        .order_by(Conversation.created_at.asc())
        .limit(limit)
    )
    messages = result.scalars().all()
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat(),
            "meta_data": msg.meta_data,
        }
        for msg in messages
    ]
