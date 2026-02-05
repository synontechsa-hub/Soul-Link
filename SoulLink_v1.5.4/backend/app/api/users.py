# /backend/app/api/users.py
# /version.py v1.5.4 Arise

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from backend.app.database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.api.dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional

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

# --- ENDPOINTS ---

@router.get("/me", response_model=UserProfile)
async def get_my_profile(user: User = Depends(get_current_user)):
    """Fetch profile for the Apartment screen."""
    return user

@router.patch("/update")
async def update_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
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
    
    return {
        "status": "Location Updated",
        "current_location": user.current_location
    }