# /backend/app/api/map.py
# /version.py v1.5.4 Arise

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from backend.app.database.session import get_async_session
from backend.app.logic.location_manager import LocationManager
from backend.app.models.location import Location
from backend.app.models.relationship import SoulRelationship
from backend.app.models.user import User
from backend.app.models.soul import SoulState
from backend.app.api.dependencies import get_current_user
from backend.app.core.rate_limiter import limiter, RateLimits
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/map", tags=["Legion Engine - Map"])

@router.get("/locations")
@limiter.limit(RateLimits.MAP_LOCATIONS)
async def get_world_map(
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session),
    request: Request = None
):
    """
    Fetch the full geography of Link City with 30-minute caching.
    """
    cache_key = "map:geography"
    
    # 1. Pull dynamic soul locations (Already cached in TimeManager)
    from backend.app.logic.time_manager import TimeManager
    time_manager = TimeManager(session)
    world_state = await time_manager.get_world_state(user.user_id)
    soul_locs = world_state['soul_locations']
    
    # 2. Check for cached geography (The static/semi-static descriptors)
    from backend.app.core.cache import cache_service
    cached_geo = cache_service.get(cache_key)
    
    if cached_geo:
        # We still need to inject the LATEST dynamic soul locations into the cached geography
        for loc in cached_geo:
            loc["present_souls"] = [s_id for s_id, l_id in soul_locs.items() if l_id == loc["id"]]
            loc["time_slot"] = world_state['time_slot']
        return cached_geo
    
    # 3. Pull all locations from the DB if cache miss
    statement = select(Location)
    res = await session.execute(statement)
    locations = res.scalars().all()
    
    # 4. Build the response
    output = []
    for loc in locations:
        output.append({
            "id": loc.location_id,
            "name": loc.display_name,
            "category": loc.category,
            "desc": loc.description,
            "privacy": loc.system_modifiers.get("privacy_gate", "Public")
            # present_souls and time_slot added in the inject step below
        })
        
    # Cache the geography for 30 minutes (semistatic)
    cache_service.set(cache_key, output, ttl=1800)
    
    # Re-inject souls for this specific request
    for loc in output:
        loc["present_souls"] = [s_id for s_id, l_id in soul_locs.items() if l_id == loc["id"]]
        loc["time_slot"] = world_state['time_slot']
        
    return output

@router.post("/move")
async def move_to_location(
    soul_id: str,
    location_id: str,
    user: User = Depends(get_current_user), 
    session: AsyncSession = Depends(get_async_session)
):
    """
    Move a soul to a new location in Link City.
    The LocationManager handles Gatekeeper rules (Privacy/Intimacy).
    """
    manager = LocationManager(session)
    
    success, message = await manager.move_to(user.user_id, soul_id, location_id)
    
    if not success:
        raise HTTPException(status_code=403, detail=message)
    
    loc = await session.get(Location, location_id)
    if not loc:
        raise HTTPException(status_code=404, detail="Destination location does not exist.")
    
    return {
        "status": "moved",
        "soul_id": soul_id,
        "new_location": loc.display_name,
        "privacy": loc.system_modifiers.get("privacy_gate", "Public"),
        "description": loc.description
    }