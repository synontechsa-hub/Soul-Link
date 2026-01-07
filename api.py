# api.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional

from roster_loader import load_roster
from onboarding import start_onboarding
from main import explore_roster
from chat_engine import start_chat
from progression import check_unlocks

app = FastAPI(title="SoulLink Backend API", version="1.2.0")

# CORS for Flutter (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later (e.g., http://localhost:3000 or your device IP)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory state (simple for testing; replace with persistence later)
STATE: Dict[str, Any] = {
    "user_state": None,
    "roster": []
}

@app.on_event("startup")
def startup():
    # Load roster once at startup
    STATE["roster"] = load_roster()

@app.post("/onboarding")
def onboarding(payload: Dict[str, Any] = Body(...)):
    """
    Payload: { "name": str, "age": str, "gender": str }
    Returns: user_state dict
    """
    name = payload.get("name", "")
    age_input = payload.get("age", "")
    gender_input = payload.get("gender", "")
    STATE["user_state"] = start_onboarding(name, age_input, gender_input)
    return {"user_state": STATE["user_state"]}

@app.get("/roster")
def roster():
    """
    Returns enriched roster for frontend rendering.
    """
    if STATE["user_state"] is None:
        return {"error": "Onboarding not completed yet."}
    enriched = explore_roster(STATE["roster"], STATE["user_state"])
    return {"roster": enriched}

@app.post("/chat")
def chat(payload: Dict[str, Any] = Body(...)):
    """
    Payload: { "bot_name": str, "message": str }
    Returns: { bot_reply, milestone, affection }
    """
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
    """
    Checks unlocks based on current user_state and roster.
    Returns: { unlocked: [bot_names] }
    """
    if STATE["user_state"] is None:
        return {"error": "Onboarding not completed yet."}
    unlocked = check_unlocks(STATE["user_state"], STATE["roster"])
    return {"unlocked": unlocked}

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.2.0"}