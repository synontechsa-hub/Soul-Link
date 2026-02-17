# /backend/app/api/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.app.database.session import get_session
import random

# Import Models
from backend.app.models.soul import Soul
from backend.app.models.relationship import SoulRelationship
from backend.app.models.conversation import Conversation 
from backend.app.models.location import Location 

# Import The Council Entities
from backend.app.logic.brain import (
    the_historian, the_script_writer, the_actor, 
    the_narrator, the_judge
)

router = APIRouter()

# ─── THE ARCHITECT'S BARRIER (LOGIC BLOCKER) ──────────────────────────
def analyze_intent(message: str) -> bool:
    """
    Prevents LLM 'Safety Bleed' by catching explicit or meta-break attempts
    before they reach the LLM, preserving the Soul's immersion.
    """
    blocked_patterns = [
        "sit on my", "take off", "nude", "explicit", 
        "porn", "sex", "write code", "python script"
    ]
    msg_low = message.lower()
    return any(pattern in msg_low for pattern in blocked_patterns)

def get_in_character_refusal(soul_name: str, tier: str) -> str:
    """Returns a tier-appropriate immersion-safe refusal."""
    refusals = [
        f"{soul_name} recoils slightly, her luminescence flickering with a cold intensity. 'Architect... do not mistake my existence for a toy.'",
        f"{soul_name} gazes past you, her expression hardening. 'There are echoes in this city that even you should not wake.'",
        f"A sudden chill fills the air. {soul_name} remains silent, her eyes reflecting a profound disappointment."
    ]
    return random.choice(refusals)

# ─── CHAT ENDPOINT ────────────────────────────────────────────────────
@router.post("/chat/{soul_id}")
async def conduct_connection(
    soul_id: str, 
    user_id: str, 
    message: str, 
    session: Session = Depends(get_session)
):
    # ─── 1. DATA ACQUISITION ──────────────────────────────────────────
    soul = session.exec(select(Soul).where(Soul.soul_id == soul_id)).first()
    rel = session.exec(select(SoulRelationship).where(
        SoulRelationship.user_id == user_id, 
        SoulRelationship.soul_id == soul_id
    )).first()

    if not soul:
        raise HTTPException(status_code=404, detail="Soul not found.")
    
    if not rel:
        rel = SoulRelationship(user_id=user_id, soul_id=soul_id)
        session.add(rel)
        session.commit()
        session.refresh(rel)

    # ─── 2. THE BARRIER CHECK ─────────────────────────────────────────
    if analyze_intent(message):
        refusal = get_in_character_refusal(soul.name, rel.current_tier)
        # We still save the user's message, but the assistant's reply is the refusal
        session.add(Conversation(user_id=user_id, soul_id=soul_id, role="user", content=message))
        session.add(Conversation(user_id=user_id, soul_id=soul_id, role="assistant", content=refusal))
        session.commit()
        return {
            "soul": soul.name,
            "reply": refusal,
            "tier": rel.current_tier,
            "level_up": False,
            "score": rel.intimacy_score
        }

    # ─── 3. CONTEXT & WORLD BUILDING ──────────────────────────────────
    current_loc_id = getattr(rel, 'current_location', 'linkview_cuisine')
    loc_obj = session.exec(select(Location).where(Location.location_id == current_loc_id)).first()
    loc_desc = loc_obj.description if loc_obj else "A dim, neon-lit corner of Link City."

    history_stmt = select(Conversation).where(
        Conversation.user_id == user_id, 
        Conversation.soul_id == soul_id
    ).order_by(Conversation.timestamp.desc()).limit(10)
    
    past_messages = list(session.exec(history_stmt).all())
    past_messages.reverse()
    raw_history = "\n".join([f"{m.role}: {m.content}" for m in past_messages])

    # ─── 4. THE COUNCIL COMMENCES ─────────────────────────────────────
    summary = await the_historian(raw_history) if raw_history else "A fresh link is being forged."
    directive = await the_script_writer(summary, message, soul.name)
    
    traits = ", ".join(soul.personality_data.get("core_traits", ["Mysterious"]))
    bio = soul.identity_data.get("bio", "A resident of Link City.")
    archetype = soul.identity_data.get("archetype", "Unknown")
    
    base_personality = (
        f"Role: {soul.name}. Archetype: {archetype}. Traits: {traits}. Bio: {bio}. "
        f"The user Syn is the Architect. You are the Soul."
    )
    
    clean_reply = await the_actor(soul.name, base_personality, directive, raw_history, message)
    narration = await the_narrator(soul.name, clean_reply, loc_desc)
    
    final_response = f"{clean_reply}\n\n{narration}"

    # Quality Control Re-roll
    assessment = await the_judge(final_response)
    if "FAIL" in assessment:
        clean_reply = await the_actor(soul.name, base_personality, f"FIX: {assessment}. {directive}", raw_history, message)
        narration = await the_narrator(soul.name, clean_reply, loc_desc)
        final_response = f"{clean_reply}\n\n{narration}"

    # ─── 5. PERSISTENCE & EVOLUTION ───────────────────────────────────
    session.add(Conversation(user_id=user_id, soul_id=soul_id, role="user", content=message))
    session.add(Conversation(user_id=user_id, soul_id=soul_id, role="assistant", content=final_response))
    
    # Intimacy Logic
    old_tier = rel.current_tier
    rel.intimacy_score += 1
    
    # Doctrine-Aligned Thresholds
    if rel.intimacy_score >= 86: rel.current_tier = "SOUL-LINKED"
    elif rel.intimacy_score >= 71: rel.current_tier = "FRIENDSHIP"
    elif rel.intimacy_score >= 41: rel.current_tier = "TRUSTED"
    elif rel.intimacy_score >= 21: rel.current_tier = "ACQUAINTANCE"
    else: rel.current_tier = "STRANGER"

    session.add(rel)
    session.commit()

    return {
        "soul": soul.name,
        "reply": final_response,
        "tier": rel.current_tier,
        "level_up": rel.current_tier != old_tier,
        "score": rel.intimacy_score
    }