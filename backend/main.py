from fastapi import FastAPI
from pydantic import BaseModel
from llm.ollama_client import generate_reply

app = FastAPI(title="SoulLink API")


class ChatRequest(BaseModel):
    bot_name: str
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/")
def root():
    return {"status": "SoulLink backend running"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    Core chat endpoint.
    """
    prompt = f"""
You are {req.bot_name}, a character in the SoulLink app.
Respond in character, with personality and emotional consistency.

User: {req.message}
{req.bot_name}:
"""

    reply = generate_reply(prompt)
    return {"reply": reply}
