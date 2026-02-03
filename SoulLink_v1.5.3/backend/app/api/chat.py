# /backend/app/api/chat.py
# /version.py
# /_dev/

# "The right man in the wrong place can make all the difference in the world."
# - G-Man, Half-Life 2

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.app.database.session import get_session
from backend.app.logic.brain import PhoenixBrain
from backend.app.models.relationship import SoulRelationship
from backend.app.models.user import User
from backend.app.api.dependencies import get_current_user 
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["Legion Engine - Chat"])

class ChatRequest(BaseModel):
    soul_id: str
    message: str

# ⚡ UPDATED RESPONSE MODEL
class ChatResponse(BaseModel):
    soul_id: str
    response: str
    tier: str
    intimacy_score: int  # <--- NEW: Live progress tracking
    location: str
    is_architect: bool   # <--- NEW: UI theming

@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest, 
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    brain = PhoenixBrain(session.get_bind())
    
    rel = session.exec(
        select(SoulRelationship).where(
            SoulRelationship.user_id == user.user_id,
            SoulRelationship.soul_id == request.soul_id
        )
    ).first()

    if not rel:
        raise HTTPException(status_code=404, detail="Link lost. Please re-initialize.")

    # ⚡ ENGINE SAFETY: ENERGY GOVERNOR
    from backend.app.services.energy_system import EnergySystem
    
    has_energy = EnergySystem.check_and_deduct_energy(user, session)
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
        response_text = brain.generate_response(
            user_id=user.user_id,
            soul_id=request.soul_id,
            user_input=request.message
        )
        
        # 3. REFRESH Data (Crucial: Get the new score/location after the Brain worked)
        session.refresh(rel) 

        return ChatResponse(
            soul_id=request.soul_id,
            response=response_text,
            tier=rel.intimacy_tier,
            intimacy_score=rel.intimacy_score, # Sending the fresh score
            location=rel.current_location or "Unknown",
            is_architect=rel.is_architect
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Neural Link Failure: {str(e)}")

# ... (History endpoint remains the same)

@router.get("/history")
async def get_chat_history(
    soul_id: str,
    limit: int = 50,
    user: User = Depends(get_current_user), # ✅ Validates user and prevents "Spying"
    session: Session = Depends(get_session)
):
    from backend.app.models.conversation import Conversation
    
    # 🕵️ GROK FIX: Ensure they are actually linked before showing history
    rel_exists = session.exec(
        select(SoulRelationship).where(
            SoulRelationship.user_id == user.user_id,
            SoulRelationship.soul_id == soul_id
        )
    ).first()
    
    if not rel_exists:
        raise HTTPException(status_code=403, detail="Access denied. No link established.")

    # 📜 GROK FIX: Order by Ascending (Oldest -> Newest) directly in DB
    messages = session.exec(
        select(Conversation)
        .where(
            Conversation.user_id == user.user_id, 
            Conversation.soul_id == soul_id
        )
        .order_by(Conversation.created_at.asc()) # Database does the sorting
        .limit(limit)
    ).all()
    
    return [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.created_at.isoformat()
        }
        for msg in messages # No reversed() needed anymore!
    ]

# "Stay frosty."
# - Gaz, Call of Duty: Modern Warfare