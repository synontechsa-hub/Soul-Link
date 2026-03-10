# /backend/app/api/locations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..database.session import get_session
from ..models.location import Location

router = APIRouter()

# "The right man in the wrong place can make all the difference in the world." 
# - G-man - Half-Life 2
@router.get("/locations/{location_id}")
def get_location(location_id: str, session: Session = Depends(get_session)):
    statement = select(Location).where(Location.location_id == location_id)
    location = session.exec(statement).first()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found.")
        
    # - "You must construct additional pylons." 
    # - Protoss - Starcraft     
    return location