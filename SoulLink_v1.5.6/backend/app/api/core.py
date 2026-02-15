# /backend/app/api/core.py
from fastapi import APIRouter
from version import VERSION_SHORT

router = APIRouter(prefix="/core", tags=["Legion Engine - Core"])

@router.get("/config")
async def get_global_config():
    return {
        "version": VERSION_SHORT,
        "maintenance_mode": False,
        "features": {
            "nsfw_unlocked": True, # The big one!
            "map_enabled": True,
            "architect_mode": True
        }
    }