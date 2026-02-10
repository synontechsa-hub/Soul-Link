# /backend/app/api/health.py
# v1.5.5 - Health Check & Metrics Endpoint
# "The first step to fixing a problem is knowing you have one."

"""
Health Check & Metrics API
Provides system status, connection counts, and performance metrics.
Essential for monitoring and alerting.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.app.database.session import get_async_session
from backend.app.services.websocket_manager import websocket_manager
from backend.app.core.cache import cache_service
from datetime import datetime
import psutil
import os

router = APIRouter(prefix="/health", tags=["Health & Monitoring"])

@router.get("")
async def health_check(session: AsyncSession = Depends(get_async_session)):
    """
    Basic health check endpoint.
    Returns 200 if system is healthy, 503 if degraded.
    
    Used by load balancers and monitoring systems.
    """
    status = "healthy"
    checks = {}
    
    # 1. Database connectivity
    try:
        result = await session.execute(text("SELECT 1"))
        result.fetchone()
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        status = "degraded"
    
    # 2. Cache connectivity
    try:
        cache_service.set("health_check", "ok", ttl=10)
        cache_value = cache_service.get("health_check")
        checks["cache"] = "ok" if cache_value == "ok" else "degraded"
    except Exception as e:
        checks["cache"] = f"error: {str(e)}"
        status = "degraded"
    
    # 3. WebSocket manager
    try:
        ws_count = websocket_manager.get_connection_count()
        ws_users = websocket_manager.get_user_count()
        checks["websocket"] = {
            "status": "ok",
            "connections": ws_count,
            "users": ws_users
        }
    except Exception as e:
        checks["websocket"] = f"error: {str(e)}"
        status = "degraded"
    
    response = {
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }
    
    # Return 503 if degraded (for load balancer health checks)
    status_code = 200 if status == "healthy" else 503
    
    from fastapi.responses import JSONResponse
    return JSONResponse(content=response, status_code=status_code)


@router.get("/metrics")
async def get_metrics(session: AsyncSession = Depends(get_async_session)):
    """
    Detailed system metrics for monitoring dashboards.
    Includes performance, resource usage, and connection stats.
    """
    
    # 1. WebSocket metrics
    ws_metrics = {
        "total_connections": websocket_manager.get_connection_count(),
        "unique_users": websocket_manager.get_user_count()
    }
    
    # 2. Database metrics
    try:
        # Count active souls
        souls_result = await session.execute(text("SELECT COUNT(*) FROM souls"))
        souls_count = souls_result.scalar()
        
        # Count active users
        users_result = await session.execute(text("SELECT COUNT(*) FROM users"))
        users_count = users_result.scalar()
        
        # Count conversations today
        convos_result = await session.execute(
            text("SELECT COUNT(*) FROM conversations WHERE DATE(created_at) = CURRENT_DATE")
        )
        convos_today = convos_result.scalar()
        
        db_metrics = {
            "souls": souls_count,
            "users": users_count,
            "conversations_today": convos_today
        }
    except Exception as e:
        db_metrics = {"error": str(e)}
    
    # 3. System metrics (CPU, Memory)
    try:
        process = psutil.Process(os.getpid())
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent()
        }
    except Exception as e:
        system_metrics = {"error": str(e)}
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "websocket": ws_metrics,
        "database": db_metrics,
        "system": system_metrics
    }


@router.get("/ready")
async def readiness_check(session: AsyncSession = Depends(get_async_session)):
    """
    Kubernetes-style readiness probe.
    Returns 200 only if the service can handle requests.
    """
    try:
        # Quick DB check
        await session.execute(text("SELECT 1"))
        
        # Check if we're not overloaded
        ws_count = websocket_manager.get_connection_count()
        if ws_count > 500:  # Arbitrary limit
            return JSONResponse(
                content={"status": "overloaded", "connections": ws_count},
                status_code=503
            )
        
        return {"status": "ready"}
    
    except Exception as e:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content={"status": "not_ready", "error": str(e)},
            status_code=503
        )
