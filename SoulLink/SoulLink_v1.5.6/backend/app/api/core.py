# /backend/app/api/core.py
from fastapi import APIRouter
from version import VERSION_SHORT
from backend.app.core.config import settings

router = APIRouter(prefix="/core", tags=["Legion Engine - Core"])


@router.get("/config")
async def get_global_config():
    """
    Public app config. Exposes only safe fields.
    debug/environment are never exposed, even in dev.
    """
    return {
        "version": VERSION_SHORT,
        "features": {
            "map_enabled": True,
            "architect_mode": True
        }
    }
