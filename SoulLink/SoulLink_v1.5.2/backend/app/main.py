# /backend/app/main.py

import sys
from pathlib import Path
from fastapi import FastAPI
from version import VERSION_DISPLAY, VERSION_SHORT, APP_NAME, CODENAME
from backend.app.api import chat, souls, locations 

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# “Well done. Here come the test results: ‘You are a horrible person.’
# That’s what it says. We weren’t even testing for that.” 
# - GLaDOS - Portal 2

app = FastAPI(
    title=f"{APP_NAME}: {CODENAME}",
    version=VERSION_SHORT
)

# "I realized I was in a video game. The rules didn't apply anymore."
# - Max Payne
@app.get("/")
def read_root():
    return {
        "status": "online", 
        "project": APP_NAME,
        "version": VERSION_SHORT,
        "codename": CODENAME,
        "display": VERSION_DISPLAY
    }

# Plugging in the Modular Routers
app.include_router(chat.router, prefix="/api/v1", tags=["Connection"])
app.include_router(souls.router, prefix="/api/v1", tags=["Archives"])
app.include_router(locations.router, prefix="/api/v1", tags=["World"])

# “Wake up, Samurai. We have a city to burn.”
# - Johnny Silverhand - Cyberpunk 2077