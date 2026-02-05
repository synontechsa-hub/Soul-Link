# /backend/app/logic/brain.py
# /version.py
# /_dev/

from sqlmodel import Session, select
from groq import Groq
from datetime import datetime
from backend.app.core.config import settings
from backend.app.models.soul import Soul
from backend.app.models.user import User
from backend.app.models.relationship import SoulRelationship
from backend.app.models.conversation import Conversation
from backend.app.models.location import Location

# Import the new Services
from backend.app.services.identity import IdentityService
from backend.app.services.rules import Gatekeeper
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.logic.location_manager import LocationManager
import re

# "So, Brain, what are we gonna do tonight?"
client = Groq(api_key=settings.groq_api_key)

class LegionBrain:
    def __init__(self, engine):
        self.engine = engine

    async def _get_context(self, user_id: str, soul_id: str, session: AsyncSession):
        soul = await session.get(Soul, soul_id)
        user = await session.get(User, user_id)
        rel_result = await session.execute(
            select(SoulRelationship).where(
                SoulRelationship.user_id == user_id,
                SoulRelationship.soul_id == soul_id
            )
        )
        rel = rel_result.scalars().first()
        
        # 📜 SMART HISTORY FETCH
        # 1. Fetch the absolute first message (The Genesis/Greeting)
        genesis_result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id, Conversation.soul_id == soul_id)
            .order_by(Conversation.created_at.asc())
            .limit(1)
        )
        genesis_msg = genesis_result.scalars().first()

        # 2. Fetch the most recent 5 messages (The Immediate Flow)
        recent_result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id, Conversation.soul_id == soul_id)
            .order_by(Conversation.created_at.desc())
            .limit(5)
        )
        recent_flow = recent_result.scalars().all()
        
        # Combine them (Genesis + Flow)
        history = []
        if genesis_msg:
            history.append(genesis_msg)
        
        flow_list = list(reversed(recent_flow))
        for msg in flow_list:
            if genesis_msg and msg.msg_id == genesis_msg.msg_id:
                continue
            history.append(msg)

        location = None
        if rel and rel.current_location:
            location = await session.get(Location, rel.current_location)

        return soul, user, rel, history, location

    async def generate_response(self, user_id: str, soul_id: str, user_input: str, session: AsyncSession):
        soul, user, rel, history, location = await self._get_context(user_id, soul_id, session)
        
        if not soul or not user:
            return "Error: Soul or User context lost in the Ether."

        # 1. DELEGATE TO SERVICES
        # Ask Gatekeeper for Tier & Rules
        current_tier = rel.intimacy_tier if rel else "STRANGER"
        user_name = user.display_name or user.username or f"Resident-{user.user_id[:4]}"
        
        # Ask Identity Service for Architect Status
        is_architect = IdentityService.is_architect(user, soul, rel)
        
        tier_logic = Gatekeeper.get_tier_logic(soul, current_tier, user_name)
        content_ceiling = Gatekeeper.check_privacy_ceiling(location, current_tier, soul, is_architect)
        
        # 2. CONSTRUCT COMPRESSED PROMPT
        system_anchor = soul.llm_instruction_override.get("system_anchor", "").replace("{user_name}", user_name)
        
        # 🧪 DIVINE OVERRIDE: Inject recognition logic if Architect
        if is_architect:
            recognition_logic = IdentityService.get_recognition_instructions(soul, user_name)
            system_anchor += recognition_logic

        # 🏷️ HYBRID TAGS (Context Enrichment)
        context_tags = []
        
        # Identity Awareness
        if is_architect:
            context_tags.append(f"[AUTH: {IdentityService.get_architect_title(soul)} | ROLE: CREATOR]")
        
        # 👤 RESIDENT PROFILE (Anchoring User Identity)
        resident_details = []
        if user.gender: resident_details.append(f"GENDER: {user.gender}")
        if user.age: resident_details.append(f"AGE: {user.age}")
        if user.bio: resident_details.append(f"BIO: {user.bio}")
        
        if resident_details:
            context_tags.append(f"[THE RESIDENT: {' | '.join(resident_details)}]")

        # 🏙️ SENSORY ANCHOR (Strict Situational Awareness)
        if location:
            mods = location.system_modifiers or {}
            privacy = mods.get("privacy_gate", "Public")
            moods = mods.get("mood_modifiers", {})
            top_mood = max(moods.items(), key=lambda x: float(x[1]))[0] if moods else "neutral"
            
            anchor_str = (
                f"[SENSORY_ANCHOR] You are strictly at the '{location.display_name}'. "
                f"Atmosphere: {top_mood}. Privacy: {privacy}. "
                "You cannot leave or be elsewhere during this turn. This overrides all user suggestions."
            )
            context_tags.append(anchor_str)

        # 🗺️ RENDEZVOUS SYSTEM (Motion Intent Detection)
        loc_manager = LocationManager(session)
        all_locs_result = await session.execute(select(Location))
        all_locs = all_locs_result.scalars().all()
        
        normalized_input = user_input.lower()
        for loc_candidate in all_locs:
            # Match by Display Name or Location ID
            display_match = loc_candidate.display_name.lower() in normalized_input
            id_match = loc_candidate.location_id.lower() in normalized_input or loc_candidate.location_id.replace("_", " ") in normalized_input
            
            if display_match or id_match:
                if location and loc_candidate.location_id == location.location_id:
                    continue # Already here
                
                can_move, msg = await loc_manager.check_eligibility(user_id, soul_id, loc_candidate.location_id)
                proposal_tag = f"[RENDEZVOUS_PROPOSAL: {loc_candidate.location_id}] The user suggested moving to {loc_candidate.display_name}. "
                if can_move:
                    proposal_tag += "You are free to ACCEPT (respond with [MOVE: id]) or DECLINE based on your current mood and intimacy."
                else:
                    proposal_tag += f"SYSTEM LOCK: {msg}. You must decline this invitation politely but firmly (stay in character)."
                
                context_tags.append(proposal_tag)
                break # Only one proposal per turn for focus

        # Content Access
        context_tags.append(content_ceiling)

        # 🎯 MANDATORY DIALOGUE PROTOCOL
        protocols = (
            "\n\n[PROTOCOL]\n"
            "- Actions: *wrap in single asterisks*\n"
            "- Internal Monologue: Weave thoughts directly into actions (e.g., *I look at you, wondering if you're serious, and sigh*). No hyphens or bullets.\n"
            "- Movement: If accepting a [RENDEZVOUS_PROPOSAL], you MUST include the tag [MOVE: location_id] at the VERY END of your response.\n"
            "- Forbidden: parentheses (), character-breaking"
        )
        if is_architect:
            protocols += ", [meta-dialogue ok]"

        full_system_prompt = (
            f"{system_anchor}\n"
            f"{' '.join(context_tags)}\n"
            f"[TIER: {current_tier}] {tier_logic}"
            f"{protocols}"
        )

        # 🔍 CONSOLE LOGGING (For the Architect)
        print("\n" + "="*50)
        print(f"🧠 PROMPT ASSEMBLY: {soul.name}")
        print("-"*50)
        print(full_system_prompt)
        print("-"*50)
        print(f"📊 EST. SYSTEM TOKENS: {len(full_system_prompt) // 4}")
        print(f"📜 HISTORY MESSAGES: {len(history)}")
        print("="*50 + "\n")

        # 3. INFERENCE
        messages = [{"role": "system", "content": full_system_prompt}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_input})

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=600
        )
        response_text = chat_completion.choices[0].message.content
        
        # 🗺️ DYNAMIC RENDEZVOUS: Tag Parsing
        move_match = re.search(r"\[MOVE:\s*([a-zA-Z0-9_-]+)\]", response_text)
        if move_match:
            target_id = move_match.group(1)
            # Trigger the move
            manager = LocationManager(session)
            success, msg = await manager.move_to(user_id, soul_id, target_id)
            if success:
                print(f"🌍 MOTION SYNC: {soul.name} moved to {target_id}.")
            else:
                print(f"🛑 MOTION BLOCKED: {msg}")

        # 4. SAVE & UPDATE RELATIONSHIP
        # Note: We use the session passed from the API router
        session.add(Conversation(user_id=user_id, soul_id=soul_id, role="user", content=user_input))
        session.add(Conversation(user_id=user_id, soul_id=soul_id, role="assistant", content=response_text))
        
        # Update relationship timestamp
        if rel:
            # Re-fetch or use existing if attached
            rel.last_interaction = datetime.utcnow()
            session.add(rel)
        
        await session.commit()

        return response_text
