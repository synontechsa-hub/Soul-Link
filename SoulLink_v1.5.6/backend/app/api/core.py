# /backend/app/api/core.py
from fastapi import APIRouter
from version import VERSION_SHORT
from backend.app.core.config import settings

router = APIRouter(prefix="/core", tags=["Legion Engine - Core"])

@router.get("/config")
async def get_global_config():
    return {
        "version": VERSION_SHORT,
        "environment": settings.environment,
        "features": {
            "nsfw_unlocked": settings.debug, # Gated by debug for alpha
            "map_enabled": True,
            "architect_mode": True
        }
    }