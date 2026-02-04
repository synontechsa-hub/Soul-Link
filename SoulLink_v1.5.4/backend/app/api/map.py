# /backend/app/api/map.py
# version.py
# _dev/

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.app.database.session import get_session
from backend.app.logic.location_manager import LocationManager
from backend.app.models.location import Location
from backend.app.models.relationship import SoulRelationship
from backend.app.models.user import User
from backend.app.api.dependencies import get_current_user 

router = APIRouter(prefix="/map", tags=["Legion Engine - Map"])

@router.get("/locations")
async def get_world_map(
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """
    Fetch the full geography of Link City directly from the Database.
    Also detects which souls are currently active in each district based on
    the current time slot and their daily routines.
    """
    # 1. Pull all locations from the DB
    statement = select(Location)
    locations = session.exec(statement).all()
    
    # 2. Get time-based soul locations using TimeManager
    from backend.app.logic.time_manager import TimeManager
    time_manager = TimeManager(session.get_bind())  # Pass engine/connection
    world_state = time_manager.get_world_state(user.user_id)
    
    # world_state contains:
    # - current_time_slot: str
    # - soul_locations: {soul_id: location_id}
    
    # 3. Build the response with time-based soul presence
    output = []
    soul_locs = world_state['soul_locations']
    
    for loc in locations:
        # Filter souls that are at this specific location
        present_souls = [s_id for s_id, l_id in soul_locs.items() if l_id == loc.location_id]
        
        output.append({
            "id": loc.location_id,
            "name": loc.display_name,
            "category": loc.category,
            "desc": loc.description,
            "privacy": loc.system_modifiers.get("privacy_gate", "Public"),
            "present_souls": present_souls,  # 📡 Time-based soul presence!
            "time_slot": world_state['time_slot']  # Current time context
        })
        
    return output

@router.post("/move")
async def move_to_location(
    soul_id: str,
    location_id: str,
    user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """
    Move a soul to a new location in Link City.
    The LocationManager handles Gatekeeper rules (Privacy/Intimacy).
    """
    manager = LocationManager(session.get_bind())
    
    success, message = manager.move_to(user.user_id, soul_id, location_id)
    
    if not success:
        raise HTTPException(status_code=403, detail=message)
    
    loc = session.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Destination location does not exist.")
    
    return {
        "status": "moved",
        "soul_id": soul_id,
        "new_location": loc.display_name,
        "privacy": loc.system_modifiers.get("privacy_gate", "Public"),
        "description": loc.description
    }