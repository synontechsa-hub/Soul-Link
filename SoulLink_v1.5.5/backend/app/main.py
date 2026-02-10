# /backend/app/main.py
# /version.py
# /_dev/

# "Despite everything, it's still you." - Undertale

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
import os
import logging

# Import the Clean Routers
from backend.app.api import chat, map, souls, sync, users, time
from backend.app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from backend.app.core.config import settings
from backend.app.core.logging_config import setup_logging
import logging

# Initialize structured logging
setup_logging(debug=settings.debug)
logger = logging.getLogger("SoulLink.Main")
from version import APP_NAME, VERSION_SHORT, VERSION_DISPLAY, CURRENT_CODENAME
import sentry_sdk

# SENTRY ERROR MONITORING
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0, # Capture 100% of transactions for development
        send_default_pii=True,
        environment=settings.environment,
        release=f"{APP_NAME}@{VERSION_SHORT}"
    )
    logger.info("✅ Sentry Integration: Active")
else:
    logger.warning("[WARN] Sentry DSN not set - Error tracking disabled")

from contextlib import asynccontextmanager
import asyncio
from backend.app.services.backup_service import BackupService
from backend.app.logic.time_manager import TimeManager
from backend.app.database.session import async_session_maker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP:
    logger.info("Initializing Legion Engine...")
    
    # 1. Warm World State Cache
    try:
        async with async_session_maker() as session:
            tm = TimeManager(session)
            await tm.warm_world_state_cache()
    except Exception as e:
        logger.warning(f"Cache Warming Failed: {e}")

    # 2. Schedule Automated Backups
    async def schedule_backups():
        while True:
            try:
                # Run backup immediately on startup (idempotent checks can be added later if needed)
                # or simpler: just run it. The service prunes old ones, so it's safe.
                # For Alpha: Run once on startup, then every 24h.
                await BackupService.perform_full_backup()
                
                # Sleep for 24 hours
                await asyncio.sleep(86400) 
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Backup Scheduler Error: {e}")
                # Retry in 1 hour if failed
                await asyncio.sleep(3600)

    # Start the background task
    backup_task = asyncio.create_task(schedule_backups())
    
    yield
    
    # SHUTDOWN:
    logger.info("Shutting down Legion Engine...")
    backup_task.cancel()
    try:
        await backup_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title=f"{APP_NAME} {CURRENT_CODENAME} v{VERSION_SHORT}",
    description="The Legion Engine - Hardened & Scalable",
    version=VERSION_SHORT,
    lifespan=lifespan
)

logger = logging.getLogger("LegionEngine")

# RATE LIMITING INTEGRATION
if settings.enable_rate_limiting:
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    logger.info("Rate limiting enabled")

# CORS CONFIGURATION
# Production-ready CORS with environment-based origins
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",      # Flutter web dev
    "http://127.0.0.1:8080",
]

# In production, only allow specific origins
if settings.environment == "production":
    if settings.production_frontend_url:
        allowed_origins = [settings.production_frontend_url]
    else:
        # Fallback to empty list if not configured (will block all CORS)
        allowed_origins = []
        logger.warning("⚠️ Production mode but no PRODUCTION_FRONTEND_URL set!")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    max_age=600,  # Cache preflight requests for 10 minutes
)


# REQUEST SIZE LIMITING & PERFORMANCE middleware
from backend.app.middleware import RequestSizeLimitMiddleware, PerformanceMiddleware

# Order matters: Performance first (outermost), then Size Limit
app.add_middleware(PerformanceMiddleware)
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_request_size=10 * 1024 * 1024  # 10MB limit (Optimized for media)
)
logger.info("Middleware stack initialized: Performance, Size Limit (1MB)")


# (Global Request Logger replaced by PerformanceMiddleware)


# PROPER ASSET MOUNTING
# Adjusting path to go from /backend/app/ to /root/assets/
script_dir = os.path.dirname(__file__)
assets_path = os.path.abspath(os.path.join(script_dir, "../../assets"))

if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    print(f"Assets Mounted: {assets_path}")
else:
    print(f"WARNING: Asset directory not found at {assets_path}")

# Import the Clean Routers
from backend.app.api import chat, map, souls, sync, users, time, websocket, health

# ... (rest of file)

# Mount the API Doors
app.include_router(health.router, prefix="/api/v1")  # ✅ Health checks first
app.include_router(users.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(map.router, prefix="/api/v1")
app.include_router(souls.router, prefix="/api/v1")
app.include_router(sync.router, prefix="/api/v1")
app.include_router(time.router, prefix="/api/v1")
app.include_router(websocket.router, prefix="/api/v1")  # ✅ WebSocket support

# GLOBAL EXCEPTION SANITIZATION
# GLOBAL EXCEPTION HANDLING
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle standard HTTP exceptions (404, 403, 401, etc.)
    Returns a clean JSON response.
    """
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
            "timestamp": logging.Formatter().formatTime(logging.LogRecord("", 0, "", 0, "", (), None), "%Y-%m-%dT%H:%M:%S")
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors (422).
    """
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "status": "error",
            "code": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": exc.errors() 
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all for unhandled server errors (500).
    Prevents crashing and leaking sensitive info (unless dev/debug).
    """
    logger.error(f"CRITICAL FAILURE: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "A critical failure occurred in the neural link.",
            # Only show details in non-production, but for alpha we want to see them
            "details": str(exc) if settings.environment != "production" else "Contact support."
        }
    )
@app.get("/")
def read_root():
    return {
        "status": f"{CURRENT_CODENAME} Rising", 
        "version": VERSION_SHORT,
        "engine": "Legion",
        "docs": "/docs",
        "endpoints": {
            "users": "/api/v1/users",
            "souls": "/api/v1/souls",
            "chat": "/api/v1/chat",
            "map": "/api/v1/map",
            "assets": "/assets" # 📡 Now visible to the web
        }
    }