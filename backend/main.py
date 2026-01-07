from fastapi import FastAPI
from pydantic import BaseModel
from llm.ollama_client import generate

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    bot_name: str | None = None

class ChatResponse(BaseModel):
    reply: str

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    prompt = (
        "You are a friendly AI companion.\n"
        f"User: {req.message}\n"
        "Assistant:"
    )
    reply = generate(prompt)
    return ChatResponse(reply=reply)
