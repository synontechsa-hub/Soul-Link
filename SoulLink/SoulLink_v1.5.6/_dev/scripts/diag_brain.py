# /_dev/scripts/diag_brain.py
import asyncio
import sys
import os
from datetime import datetime
from sqlmodel import select, Session

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from backend.app.core.config import settings
from backend.app.database.session import engine, AsyncSession, get_async_session
from backend.app.models.user import User
from backend.app.models.soul import Soul, SoulPillar
from backend.app.models.link_state import LinkState
from backend.app.models.user_persona import UserPersona
from backend.app.logic.brain import LegionBrain

async def diag():
    print("🧠 SoulLink Brain Diagnostic")
    
    # Using a sync session for setup
    with Session(engine) as session:
        # Get Architect User
        ARCHITECT_UUID = "14dd612d-744e-487d-b2d5-cc47732183d3"
        user = session.get(User, ARCHITECT_UUID)
        if not user:
            print("❌ Architect user not found in DB.")
            return

        # Get first soul
        soul = session.execute(select(Soul)).scalars().first()
        if not soul:
            print("❌ No souls found in DB.")
            return
        
        print(f"Target Soul: {soul.name} ({soul.soul_id})")

        # Ensure LinkState exists
        link = session.execute(
            select(LinkState).where(LinkState.user_id == user.user_id, LinkState.soul_id == soul.soul_id)
        ).scalars().first()
        if not link:
            print("Creating LinkState...")
            link = LinkState(user_id=user.user_id, soul_id=soul.soul_id, signal_stability=100.0, intimacy_tier="SOUL_LINKED")
            session.add(link)
            session.commit()
            session.refresh(link)

        # Get persona
        persona = session.execute(select(UserPersona).where(UserPersona.user_id == user.user_id)).scalars().first()
        if not persona:
            print("Creating Persona...")
            persona = UserPersona(user_id=user.user_id, screen_name="Architect", bio="The creator.")
            session.add(persona)
            session.commit()
            session.refresh(persona)

    # Now test the Brain (Async)
    print("\n[TEST] Generating response...")
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        async with AsyncSession(engine) as async_session:
            brain = LegionBrain(async_session)
            # Re-fetch objects for the async session
            link = await async_session.get(LinkState, link.id)
            persona = await async_session.get(UserPersona, persona.id)
            
            response = await brain.generate_response(
                user_id=user.user_id,
                soul_id=soul.soul_id,
                user_input="Hello diagnostic tool.",
                session=async_session,
                link_state=link,
                persona=persona
            )
            print(f"✅ Brain successful. Response: {response[:50]}...")
    except Exception as e:
        import traceback
        print(f"❌ Brain failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diag())
