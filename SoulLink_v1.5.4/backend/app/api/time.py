# /backend/app/api/time.py
# /version.py v1.5.4 Arise
# /_dev/

# "What is time? A measurement of change."
# - The Doctor, Doctor Who

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel
from typing import Optional
from backend.app.database.session import get_session
from backend.app.models.user import User
from backend.app.models.time_slot import TimeSlot, get_time_slot_display_name, get_time_slot_description
from backend.app.logic.time_manager import TimeManager
from backend.app.api.dependencies import get_current_user

router = APIRouter(prefix="/time", tags=["Legion Engine - Time"])

class AdvanceTimeRequest(BaseModel):
    """Request to advance time slot"""
    target_slot: Optional[str] = None  # If None, advances to next slot

class TimeStateResponse(BaseModel):
    """Current time slot state"""
    current_slot: str
    display_name: str
    description: str
    soul_locations: dict

@router.post("/advance")
async def advance_time_slot(
    request: AdvanceTimeRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Advance the user's time slot to the next one (or jump to a specific slot).
    This is the "End Turn" mechanic - triggered by sleeping in the apartment bed.
    
    Returns the new time slot and updated world state.
    """
    manager = TimeManager(session.get_bind())
    
    # Validate target slot if provided
    target_slot_enum = None
    if request.target_slot:
        try:
            target_slot_enum = TimeSlot(request.target_slot)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time slot: {request.target_slot}. Must be one of: morning, afternoon, evening, night, home_time"
            )
    
    # Advance time
    new_slot = manager.advance_time_slot(user.user_id, target_slot_enum)
    
    # Get updated world state
    world_state = manager.get_world_state(user.user_id)
    
    return {
        "status": "time_advanced",
        "previous_slot": user.current_time_slot,
        "current_slot": new_slot.value,
        "new_time_slot": new_slot.value, # Frontend expectation fix
        "display_name": get_time_slot_display_name(new_slot),
        "description": get_time_slot_description(new_slot),
        "soul_locations": world_state["soul_locations"]
    }

@router.get("/current")
async def get_current_time_state(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> TimeStateResponse:
    """
    Get the current time slot and world state.
    Shows where all souls are right now based on their routines.
    """
    manager = TimeManager(session.get_bind())
    world_state = manager.get_world_state(user.user_id)
    
    current_slot = TimeSlot(world_state["time_slot"])
    
    return TimeStateResponse(
        current_slot=current_slot.value,
        display_name=get_time_slot_display_name(current_slot),
        description=get_time_slot_description(current_slot),
        soul_locations=world_state["soul_locations"]
    )

@router.get("/slots")
async def get_all_time_slots():
    """
    Get information about all available time slots.
    Useful for the time selection UI in the apartment.
    """
    slots = []
    for slot in TimeSlot:
        slots.append({
            "value": slot.value,
            "display_name": get_time_slot_display_name(slot),
            "description": get_time_slot_description(slot)
        })
    return {"slots": slots}
