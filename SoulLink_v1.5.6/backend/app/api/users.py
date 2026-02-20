# /backend/app/api/users.py
# /version.py v1.5.6 Normandy SR-2

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import select
from backend.app.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.api.dependencies import get_current_user
from backend.app.core.rate_limiter import limiter, RateLimits
from pydantic import BaseModel, ConfigDict
from typing import Optional
from backend.app.core.cache import cache_service

router = APIRouter(prefix="/users", tags=["Legion Engine - Users"])

# --- SCHEMAS (Data Shapes) ---

class UserUpdate(BaseModel):
    """Data sent from the Apartment Mirror to update the persona."""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None

class UserProfile(BaseModel):
    """The full data packet for the frontend."""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    username: Optional[str]
    display_name: Optional[str]
    bio: Optional[str]
    gender: Optional[str]
    age: Optional[int]
    account_tier: str
    gems: int
    energy: int
    current_location: str
    current_time_slot: str # Added to match frontend User model

# --- ENDPOINTS ---

@router.get("/me", response_model=UserProfile)
@limiter.limit(RateLimits.READ_ONLY)
async def get_my_profile(
    user: User = Depends(get_current_user),
    request: Request = None
):
    """Fetch profile for the Apartment screen."""
    cache_key = f"user:profile:{user.user_id}"
    
    # Check cache
    cached_profile = cache_service.get(cache_key)
    if cached_profile:
        return cached_profile
    
    # If not cached, the returned 'user' object will be validated against UserProfile
    # and then returned. We should cache the validated dict for maximum speed.
    profile_data = UserProfile.model_validate(user).model_dump(mode='json')
    
    cache_service.set(cache_key, profile_data, ttl=600) # 10 minute profile cache
    return profile_data


@router.get("/me/personas")
@limiter.limit(RateLimits.READ_ONLY)
async def get_my_personas(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """List all personas for the current user."""
    from backend.app.models.user_persona import UserPersona
    result = await session.execute(
        select(UserPersona).where(UserPersona.user_id == user.user_id)
    )
    personas = result.scalars().all()
    return personas


@router.patch("/me/personas/{persona_id}/activate")
@limiter.limit(RateLimits.USER_WRITE)
async def activate_persona(
    persona_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Switch the active persona for the user."""
    from backend.app.services.persona_service import PersonaService
    success = await PersonaService.set_active_persona(session, user.user_id, persona_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Persona not found or does not belong to user.")
        
    return {"success": True, "active_persona_id": persona_id}

@router.patch("/update")
@limiter.limit(RateLimits.USER_WRITE)
async def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    """THE MIRROR: Updates user persona data."""
    if data.display_name is not None:
        user.display_name = data.display_name
    if data.bio is not None:
        user.bio = data.bio
    if data.gender is not None:
        user.gender = data.gender
    if data.age is not None:
        user.age = data.age
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    # Invalidate cache
    cache_service.delete(f"user:profile:{user.user_id}")
    
    return {
        "status": "Identity Synchronized",
        "updated_fields": data.dict(exclude_none=True)
    }

class UserMove(BaseModel):
    location_id: str

@router.patch("/move")
async def move_user(
    data: UserMove,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Update the user's current location in the city.
    """
    user.current_location = data.location_id
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    # Invalidate cache
    cache_service.delete(f"user:profile:{user.user_id}")
    
    return {
        "status": "Location Updated",
        "current_location": user.current_location
    }