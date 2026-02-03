# /backend/app/main.py
# /version.py
# /_dev/

# "Despite everything, it's still you." - Undertale

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Import the Clean Routers
from backend.app.api import chat, map, souls, sync, users
from version import APP_NAME, VERSION_SHORT, VERSION_DISPLAY, CURRENT_CODENAME

app = FastAPI(
    title=f"{APP_NAME} {CURRENT_CODENAME} v{VERSION_SHORT}",
    description="The Legion Engine - Clean & Shippable",
    version=VERSION_SHORT
)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Lock this down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🖼️ PROPER ASSET MOUNTING
# Adjusting path to go from /backend/app/ to /root/assets/
script_dir = os.path.dirname(__file__)
assets_path = os.path.abspath(os.path.join(script_dir, "../../assets"))

if os.path.exists(assets_path):
    app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    print(f"✅ Assets Mounted: {assets_path}")
else:
    print(f"⚠️ WARNING: Asset directory not found at {assets_path}")

# 🚪 Mount the API Doors
app.include_router(users.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(map.router, prefix="/api/v1")
app.include_router(souls.router, prefix="/api/v1")
app.include_router(sync.router, prefix="/api/v1")

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