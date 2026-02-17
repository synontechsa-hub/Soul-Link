# /backend/app/services/persona_service.py
# v1.5.6 Identity Logic - Switching Masks

from sqlmodel import Session, select
from app.models.user_persona import UserPersona
from app.models.user import User

class PersonaService:
    """
    Manages the switching and creation of User Personas.
    Ensures only one persona is active per user.
    """
    
    @staticmethod
    def get_active_persona(session: Session, user_id: str) -> Optional[UserPersona]:
        statement = select(UserPersona).where(
            UserPersona.user_id == user_id,
            UserPersona.is_active == True
        )
        return session.exec(statement).first()

    @staticmethod
    def set_active_persona(session: Session, user_id: str, persona_id: int):
        # 1. Deactivate all for this user
        statement = select(UserPersona).where(UserPersona.user_id == user_id)
        all_personas = session.exec(statement).all()
        for p in all_personas:
            p.is_active = False
            
        # 2. Activate target
        target = session.get(UserPersona, persona_id)
        if target and target.user_id == user_id:
            target.is_active = True
            target.last_used = datetime.utcnow()
            session.add(target)
            session.commit()
            return target
        return None

    @staticmethod
    def create_default_persona(session: Session, user: User) -> UserPersona:
        """
        Migrates legacy User bio/name to a new Default Persona.
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
        session.commit()
        return new_persona
