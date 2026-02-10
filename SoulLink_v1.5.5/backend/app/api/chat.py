# /backend/app/api/chat.py
# /version.py
# /_dev/

# "The right man in the wrong place can make all the difference in the world."
# - G-Man, Half-Life 2

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from backend.app.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.logic.brain import LegionBrain
from backend.app.models.relationship import SoulRelationship
from backend.app.models.user import User
from backend.app.api.dependencies import get_current_user 
from backend.app.logic.time_manager import TimeManager
from backend.app.models.time_slot import TimeSlot
from backend.app.core.rate_limiter import limiter, RateLimits
from backend.app.core.validation import ValidatedChatRequest
from backend.app.core.logging_config import get_logger
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/chat", tags=["Legion Engine - Chat"])
logger = get_logger("ChatAPI")

# ⚡ UPDATED RESPONSE MODEL
class ChatResponse(BaseModel):
    soul_id: str
    response: str
    tier: str
    intimacy_score: int  # <--- NEW: Live progress tracking
    location: str
    is_architect: bool   # <--- NEW: UI theming
    debug_info: Optional[dict] = None # <--- NEW: Telemetry

@router.post("/send", response_model=ChatResponse)
@limiter.limit(RateLimits.CHAT)
async def send_message(
    chat_request: ValidatedChatRequest,  # ✅ Validated input
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    logger.info(f"Chat request from user={user.user_id} to soul={chat_request.soul_id}")
    brain = LegionBrain(session.bind)
    
    rel_result = await session.execute(
        select(SoulRelationship).where(
            SoulRelationship.user_id == user.user_id,
            SoulRelationship.soul_id == chat_request.soul_id
        )
    )
    rel = rel_result.scalars().first()

    if not rel:
        raise HTTPException(status_code=404, detail="Link lost. Please re-initialize.")

    # ⚡ ENGINE SAFETY: ENERGY GOVERNOR
    from backend.app.services.energy_system import EnergySystem
    
    has_energy = await EnergySystem.check_and_deduct_energy(user, session)
    if not has_energy:
        # Check if they are simply spamming
        # For MVP: Hard blocking anyone with 0 energy.
        # Future: Implement the 30s slow-lane timer.
        raise HTTPException(
            status_code=429, 
            detail="Neural Link Overheated (Zero Energy). Recharging systems..."
        )

    try:
        # 2. Generate Response (Brain might update Intimacy inside logic/brain.py)
        response_text = await brain.generate_response(
            user_id=user.user_id,
            soul_id=chat_request.soul_id,
            user_input=chat_request.message,
            session=session
        )
        
        # 3. UNIFIED LOCATION RESOLUTION
        # Manual Override > Dynamic Routine
        display_location = rel.current_location
        if not display_location:
            time_manager = TimeManager(session)
            display_location = await time_manager.get_soul_location_at_time(
                chat_request.soul_id, 
                TimeSlot(user.current_time_slot)
            )

        # 4. MONITORING (For the Architect's Eyes Only)
        debug_info = None
        if user.account_tier == "architect":
            # Roughly estimate tokens from user input + estimated base prompt
            # (Actual full prompt count is inside brain.py)
            est_base = 1200 # Average system context
            debug_info = {
                "est_input_tokens": (len(chat_request.message) // 4) + est_base,
                "model": "llama-3.3-70b-versatile",
                "status": "Telemetry Active"
            }
        
        # 5. 🚀 REAL-TIME: Push via WebSocket
        from backend.app.services.websocket_manager import websocket_manager
        from datetime import datetime
        
        await websocket_manager.send_to_user(user.user_id, {
            "type": "chat_message",
            "data": {
                "soul_id": chat_request.soul_id,
                "response": response_text,
                "intimacy_score": rel.intimacy_score,
                "tier": rel.intimacy_tier,
                "location": display_location or "Unknown"
            },
            "timestamp": datetime.utcnow().isoformat()
        })

        return ChatResponse(
            soul_id=chat_request.soul_id,
            response=response_text,
            tier=rel.intimacy_tier,
            intimacy_score=rel.intimacy_score,
            location=display_location or "Unknown",
            is_architect=rel.is_architect,
            debug_info=debug_info
        )
    except Exception as e:
        import traceback
        logger.error(f"Chat error for user={user.user_id}, soul={chat_request.soul_id}: {e}")
        logger.debug(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Neural Link Failure: {str(e)}")

# ... (History endpoint remains the same)

@router.get("/history")
@limiter.limit(RateLimits.READ_ONLY)
async def get_chat_history(
    soul_id: str,
    limit: int = 50,
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    from backend.app.models.conversation import Conversation
    
    # 🕵️ GROK FIX: Ensure they are actually linked before showing history
    rel_result = await session.execute(
        select(SoulRelationship).where(
            SoulRelationship.user_id == user.user_id,
            SoulRelationship.soul_id == soul_id
        )
    )
    rel_exists = rel_result.scalars().first()
    
    if not rel_exists:
        raise HTTPException(status_code=403, detail="Access denied. No link established.")

    # 📜 GROK FIX: Order by Ascending (Oldest -> Newest) directly in DB
    msg_result = await session.execute(
        select(Conversation)
        .where(
            Conversation.user_id == user.user_id, 
            Conversation.soul_id == soul_id
        )
        .order_by(Conversation.created_at.asc())
        .limit(limit)
    )
    messages = msg_result.scalars().all()
    
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.created_at.isoformat()
        }
        for msg in messages 
    ]

# "Stay frosty."
# - Gaz, Call of Duty: Modern Warfare