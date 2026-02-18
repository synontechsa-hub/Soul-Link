# /backend/app/services/persona_service.py
# v1.5.6 Identity Logic - Switching Masks

from datetime import datetime
from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user_persona import UserPersona
from backend.app.models.user import User

class PersonaService:
    """
    Manages the switching and creation of User Personas.
    Ensures only one persona is active per user.
    All methods are async to match the AsyncSession used in chat.py.
    """

    @staticmethod
    async def get_active_persona(session: AsyncSession, user_id: str) -> Optional[UserPersona]:
        result = await session.execute(
            select(UserPersona).where(
                UserPersona.user_id == user_id,
                UserPersona.is_active == True
            )
        )
        return result.scalars().first()

    @staticmethod
    async def set_active_persona(session: AsyncSession, user_id: str, persona_id: int) -> Optional[UserPersona]:
        # 1. Deactivate all for this user
        result = await session.execute(
            select(UserPersona).where(UserPersona.user_id == user_id)
        )
        all_personas = result.scalars().all()
        for p in all_personas:
            p.is_active = False

        # 2. Activate target
        target = await session.get(UserPersona, persona_id)
        if target and target.user_id == user_id:
            target.is_active = True
            target.last_used = datetime.utcnow()
            session.add(target)
            await session.commit()
            return target
        return None

    @staticmethod
    async def create_default_persona(session: AsyncSession, user: User) -> UserPersona:
        """
        Creates a default Persona from the legacy User bio/name fields.
        Called automatically when a user has no active persona.
        """
        new_persona = UserPersona(
            user_id=user.user_id,
            screen_name=user.username or "Linker",
            bio=user.bio,
            age=user.age,
            gender=user.gender,
            is_active=True,
            identity_anchor="The Original"
        )
        session.add(new_persona)
        await session.flush()  # Get ID without full commit
        return new_persona
