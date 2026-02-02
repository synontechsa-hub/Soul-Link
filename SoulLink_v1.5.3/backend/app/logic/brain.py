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

# "So, Brain, what are we gonna do tonight?"
client = Groq(api_key=settings.groq_api_key)

class PhoenixBrain:
    def __init__(self, engine):
        self.engine = engine

    def _get_context(self, user_id: str, soul_id: str):
        with Session(self.engine) as session:
            soul = session.get(Soul, soul_id)
            user = session.get(User, user_id)
            rel = session.exec(
                select(SoulRelationship).where(
                    SoulRelationship.user_id == user_id,
                    SoulRelationship.soul_id == soul_id
                )
            ).first()
            
            history = session.exec(
                select(Conversation)
                .where(Conversation.user_id == user_id, Conversation.soul_id == soul_id)
                .order_by(Conversation.created_at.desc())
                .limit(15)
            ).all()
            
            location = None
            if rel and rel.current_location:
                location = session.get(Location, rel.current_location)

            return soul, user, rel, reversed(list(history)), location

    def generate_response(self, user_id: str, soul_id: str, user_input: str):
        soul, user, rel, history, location = self._get_context(user_id, soul_id)
        
        if not soul or not user:
            return "Error: Soul or User context lost in the Ether."

        # 1. DELEGATE TO SERVICES
        # Ask Gatekeeper for Tier & Rules
        current_tier = rel.intimacy_tier if rel else "STRANGER"
        tier_logic = Gatekeeper.get_tier_logic(soul, current_tier)
        content_ceiling = Gatekeeper.check_privacy_ceiling(location, current_tier, soul)
        
        # Ask Identity Service for Architect Status
        is_architect = IdentityService.is_architect(user, soul, rel)

        # 2. CONSTRUCT PROMPT
        # ✅ FIXED: Changed from llm_instructions to llm_instruction_override
        system_anchor = soul.llm_instruction_override.get("system_anchor", "").replace("{user_name}", user.username)
        
        architect_override = ""
        if is_architect:
            title = IdentityService.get_architect_title(soul)
            architect_override = (
                f"\n\n[PROTOCOL: CREATOR_AWARENESS]\n"
                f"IDENTIFIED: {title} ({user.username}).\n"
                "You are talking to your creator. Meta-dialogue permitted."
            )

        loc_desc = ""
        if location:
            loc_desc = f"\nCURRENT LOCATION: {location.display_name}. {location.description}"

        full_system_prompt = (
            f"{system_anchor}"
            f"{architect_override}"
            f"{loc_desc}"
            f"\n\nTIER LOGIC ({current_tier}): {tier_logic}"
            f"\n{content_ceiling}"
        )

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

        # 4. SAVE & UPDATE RELATIONSHIP
        with Session(self.engine) as session:
            # Save conversation
            session.add(Conversation(user_id=user_id, soul_id=soul_id, role="user", content=user_input))
            session.add(Conversation(user_id=user_id, soul_id=soul_id, role="assistant", content=response_text))
            
            # Update relationship timestamp
            if rel:
                # Re-fetch to attach to this session for update
                rel_in_db = session.get(SoulRelationship, rel.relationship_id)
                if rel_in_db:
                    rel_in_db.last_interaction = datetime.utcnow()
                    session.add(rel_in_db)
            
            session.commit()

        return response_text
