# /backend/app/api/users.py
# /version.py v1.5.3-P

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.app.database.session import get_session
from backend.app.models.user import User
from backend.app.api.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional
import secrets

router = APIRouter(prefix="/users", tags=["Legion Engine - Users"])

# --- SCHEMAS (Data Shapes) ---

class UserRegistration(BaseModel):
    username: str
    display_name: Optional[str] = None

class UserUpdate(BaseModel):
    """Data sent from the Apartment Mirror to update the persona."""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    gender_identity: Optional[str] = None
    age: Optional[int] = None

class UserProfile(BaseModel):
    """The full data packet for the frontend."""
    user_id: str
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    gender_identity: Optional[str]
    age: Optional[int]
    account_tier: str
    gems: int
    energy: int

class LoginRequest(BaseModel):
    username: str

# --- ENDPOINTS ---

@router.post("/login")
async def login_user(
    data: LoginRequest, 
    session: Session = Depends(get_session)
):
    """
    Main entry point. Fetches user or handles Architect recovery.
    """
    username_clean = data.username.strip()
    
    statement = select(User).where(User.username == username_clean)
    user = session.exec(statement).first()

    if not user:
        # 👑 THE ARCHITECT RECOVERY PROTOCOL
        if username_clean.lower() in ["syn", "synonimity"]:
            user = User(
                user_id="USR-001",
                username=username_clean,
                display_name="Syn",
                account_tier="architect",
                energy=9999, # Divine energy
                bio="The Creator of Link City."
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        else:
            # Tell Flutter to show the registration prompt
            raise HTTPException(404, detail="Identity not found. Registration required.")

    return {
        "status": "Linked",
        "user_id": user.user_id,
        "username": user.username,
        "profile": user 
    }

@router.post("/register")
async def register_user(
    registration: UserRegistration,
    session: Session = Depends(get_session)
):
    """Registers a new Linker account."""
    if len(registration.username) < 3:
        raise HTTPException(400, detail="Username too short.")
    
    existing = session.exec(select(User).where(User.username == registration.username)).first()
    if existing:
        raise HTTPException(409, detail="Username taken.")
    
    # Generate a random 8-char hex for the ID
    user_id = f"USR-{secrets.token_hex(4).upper()}"
    
    new_user = User(
        user_id=user_id,
        username=registration.username,
        display_name=registration.display_name or registration.username,
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return {"status": "registered", "user_id": new_user.user_id}

@router.get("/me", response_model=UserProfile)
async def get_my_profile(user: User = Depends(get_current_user)):
    """Fetch profile for the Apartment screen."""
    return user

@router.patch("/update")
async def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """THE MIRROR: Updates user persona data."""
    if data.display_name is not None:
        user.display_name = data.display_name
    if data.bio is not None:
        user.bio = data.bio
    if data.gender_identity is not None:
        user.gender_identity = data.gender_identity
    if data.age is not None:
        user.age = data.age
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {
        "status": "Identity Synchronized",
        "updated_fields": data.dict(exclude_none=True)
    }