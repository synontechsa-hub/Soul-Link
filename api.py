# api.py
import logging
import json
from pathlib import Path
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from roster_loader import load_roster
from onboarding import start_onboarding, STATE_FILE
from main import explore_roster
from chat_engine import start_chat
from progression import check_unlocks
from version import SOUL_LINK_VERSION

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

app = FastAPI(title="SoulLink Backend API", version=SOUL_LINK_VERSION)

# CORS for Flutter (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory state
STATE: Dict[str, Any] = {
    "user_state": None,
    "roster": []
}

@app.on_event("startup")
def startup():
    # Load roster once at startup
    STATE["roster"] = load_roster()

    # Reload user profile if it exists
    if STATE_FILE.exists():
        try:
            with STATE_FILE.open("r", encoding="utf-8") as f:
                STATE["user_state"] = json.load(f)
            logging.info(f"Reloaded user profile from {STATE_FILE}")
        except Exception as e:
            logging.error(f"Failed to reload user profile: {e}")

@app.post("/onboarding")
def onboarding(payload: Dict[str, Any] = Body(...)):
    """
    Accepts either:
    { "name": str, "age": str, "gender": str }
    OR
    { "name": str, "age_input": str, "gender_input": str }
    """
    logging.info(f"Payload received: {payload}")

    name = payload.get("name", "")
    age_input = payload.get("age_input") or payload.get("age", "")
    gender_input = payload.get("gender_input") or payload.get("gender", "")

    STATE["user_state"] = start_onboarding(name, age_input, gender_input)
    return {"user_state": STATE["user_state"]}

@app.get("/roster")
def roster():
    """Returns enriched roster for frontend rendering."""
    if STATE["user_state"] is None:
        return {"error": "Onboarding not completed yet."}
    enriched = explore_roster(STATE["roster"], STATE["user_state"])
    return {"roster": enriched}

@app.post("/chat")
def chat(payload: Dict[str, Any] = Body(...)):
    """Payload: { "bot_name": str, "message": str }"""
    if STATE["user_state"] is None:
        return {"error": "Onboarding not completed yet."}

    bot_name = payload.get("bot_name")
    message = payload.get("message", "")

    # Find bot
    bot = next((b for b in STATE["roster"] if b.get("name") == bot_name), None)
    if not bot:
        return {"error": f"Bot '{bot_name}' not found."}

    # Start chat session and handle message
    chat_session = start_chat(bot, STATE["user_state"])
    result = chat_session["handle_message"](message)

    return result

@app.post("/progression")
def progression():
    """Checks unlocks based on current user_state and roster."""
    if STATE["user_state"] is None:
        return {"error": "Onboarding not completed yet."}
    unlocked = check_unlocks(STATE["user_state"], STATE["roster"])
    return {"unlocked": unlocked}

@app.get("/health")
def health():
    return {"status": "ok", "version": SOUL_LINK_VERSION}