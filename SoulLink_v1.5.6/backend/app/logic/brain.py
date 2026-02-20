# /backend/app/logic/brain.py
# v1.5.6 Normandy SR-2 Brain Logic

import logging
from sqlmodel import select
from datetime import datetime, timezone
from backend.app.core.config import settings
from backend.app.models.soul import Soul, SoulPillar
from backend.app.models.user import User
from backend.app.models.link_state import LinkState
from backend.app.models.user_persona import UserPersona
from backend.app.models.conversation import Conversation
from backend.app.models.location import Location

# Import the new Services
from backend.app.services.identity import IdentityService
from backend.app.services.context_assembler import ContextAssembler
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("LegionBrain")

class LegionBrain:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._client = None

    @property
    def client(self):
        """Lazy-loaded Groq client."""
        if self._client is None:
            from groq import Groq
            self._client = Groq(api_key=settings.groq_api_key)
        return self._client

    async def _get_context(self, user_id: str, soul_id: str, session: AsyncSession):
        soul = await session.get(Soul, soul_id)
        pillar = await session.get(SoulPillar, soul_id)
        # SoulState is now global/simulation state only. 
        # User-specific mutable state is in LinkState.
        
        # We assume LinkState is passed in or fetched. 
        # For backward compatibility within this private method, we can fetch it if needed,
        # but optimally the caller provides it.
        
        user = await session.get(User, user_id)
        
        # 📜 SMART HISTORY FETCH
        genesis_result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id, Conversation.soul_id == soul_id)
            .order_by(Conversation.created_at.asc())
            .limit(1)
        )
        genesis_msg = genesis_result.scalars().first()

        recent_result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id, Conversation.soul_id == soul_id)
            .order_by(Conversation.created_at.desc())
            .limit(10) # Bumped to 10 for better context
        )
        recent_flow = recent_result.scalars().all()
        
        history = []
        if genesis_msg:
            history.append(genesis_msg)
        
        flow_list = list(reversed(recent_flow))
        for msg in flow_list:
            if genesis_msg and msg.msg_id == genesis_msg.msg_id:
                continue
            history.append(msg)

        return soul, pillar, user, history

    async def generate_response(
        self, 
        user_id: str, 
        soul_id: str, 
        user_input: str, 
        session: AsyncSession,
        link_state: LinkState,
        persona: UserPersona,
        world_state_injection: str = ""
    ):
        """
        v1.5.6 Update: Now accepts LinkState and Persona directly.
        """
        soul, pillar, user, history = await self._get_context(user_id, soul_id, session)
        
        if not soul or not user or not pillar or not link_state:
            return "Error: Soul consciousness, pillars, or link state lost in the Ether."

        # 1. RESOLVE LOCATION
        # LinkState has the user-specific override
        current_loc_id = link_state.current_location or "soul_plaza"
        location = await session.get(Location, current_loc_id)

        # 2. ASK SERVICES
        is_architect = link_state.is_architect
        # Note: IdentityService might need refactoring too, but for now we pass what we have.
        
        # 3. BUILD PROMPT (Delegated to ContextAssembler)
        full_system_prompt = ContextAssembler.build_system_prompt(
            soul=soul,
            pillar=pillar,
            persona=persona,
            link_state=link_state,
            location=location,
            is_architect=is_architect,
            world_state=world_state_injection
        )

        # 🔍 LOGGING (v1.5.6 Hardening: replaced print with logger)
        logger.debug(f"🧠 PROMPT ASSEMBLY: {soul.name} | Persona: {persona.screen_name}")
        logger.debug(f"\nPrompt: {full_system_prompt}")

        # 4. INFERENCE
        messages = [{"role": "system", "content": full_system_prompt}]
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_input})

        # Cost-saving truncation
        if len(messages) > 12: 
            # Keep system + genesis + last 10
            messages = [messages[0]] + messages[-11:]

        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.8,
            max_tokens=600
        )
        response_text = chat_completion.choices[0].message.content
        
        # 5. SAVE & UPDATE
        # Save Conversation
        conv_user = Conversation(user_id=user_id, soul_id=soul_id, role="user", content=user_input)
        conv_assistant = Conversation(user_id=user_id, soul_id=soul_id, role="assistant", content=response_text)
        
        # v1.5.6: Store telemetry in metadata
        conv_assistant.meta_data = {
            "persona_id": persona.id,
            "link_state_id": link_state.id
        }
        
        session.add(conv_user)
        session.add(conv_assistant)
        
        # Update LinkState
        link_state.last_interaction = datetime.now(timezone.utc)
        link_state.total_messages_sent = (getattr(link_state, 'total_messages_sent', 0) or 0) + 1
        
        # Normandy-SR2 Fix: Perform stability decay inside the brain for atomic commit
        link_state.signal_stability = max(0.0, link_state.signal_stability - settings.ad_stability_decay_rate)
        
        session.add(link_state)
        
        # Update Persona Last Used
        persona.last_used = datetime.now(timezone.utc)
        session.add(persona)
        
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"❌ TRANSACTION FAILED: {e}")
            raise Exception(f"Failed to save conversation: {str(e)}")

        return response_text
