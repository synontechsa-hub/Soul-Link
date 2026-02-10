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
from version import APP_NAME, VERSION_SHORT, VERSION_DISPLAY, CURRENT_CODENAME
import sentry_sdk

# SENTRY ERROR MONITORING
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0, # Capture 100% of transactions for development
        send_default_pii=True
    )
    print("Sentry Integration: Active")

app = FastAPI(
    title=f"{APP_NAME} {CURRENT_CODENAME} v{VERSION_SHORT}",
    description="The Legion Engine - Hardened & Scalable",
    version=VERSION_SHORT
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


# REQUEST SIZE LIMITING
from backend.app.middleware import RequestSizeLimitMiddleware
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_request_size=1024 * 1024  # 1MB limit
)
logger.info("Request size limiting enabled (1MB max)")


# DEBUG: Global Request Logger
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"INCOMING: {request.method} {request.url}")
    # logger.info(f"   Headers: {request.headers}") 
    try:
        response = await call_next(request)
        logger.info(f"OUTGOING: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"MIDDLEWARE ERROR: {e}")
        raise e


# PROPER ASSET MOUNTING
# Adjusting path to go from /backend/app/ to /root/assets/
script_dir = os.path.dirname(__file__)
assets_path = os.path.abspath(os.path.join(script_dir, "../../assets"))

if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    print(f"Assets Mounted: {assets_path}")
else:
    print(f"WARNING: Asset directory not found at {assets_path}")

# Mount the API Doors
app.include_router(users.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(map.router, prefix="/api/v1")
app.include_router(souls.router, prefix="/api/v1")
app.include_router(sync.router, prefix="/api/v1")
app.include_router(time.router, prefix="/api/v1")

# GLOBAL EXCEPTION SANITIZATION
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Simplified logging to avoid UnicodeEncodeError on Windows
    logger.error(f"NEURAL LINK CRITICAL FAILURE: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "A critical failure occurred in the neural link.",
            "details": str(exc) # Explicitly return error details to frontend for debugging
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