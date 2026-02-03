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
    Also detects which souls are currently active in each district.
    """
    # 1. Pull all locations from the DB
    statement = select(Location)
    locations = session.exec(statement).all()
    
    # 2. Pull all relationships for this user to see where souls are
    rel_statement = select(SoulRelationship).where(SoulRelationship.user_id == user.user_id)
    relationships = session.exec(rel_statement).all()
    
    # 3. Build the response
    output = []
    for loc in locations:
        # Check if any of your souls are here
        present_souls = [
            rel.soul_id for rel in relationships 
            if rel.current_location == loc.location_id
        ]
        
        output.append({
            "id": loc.location_id,
            "name": loc.display_name,
            "category": loc.category,
            "desc": loc.description,
            "privacy": loc.system_modifiers.get("privacy_gate", "Public"),
            "present_souls": present_souls # 📡 Live data!
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