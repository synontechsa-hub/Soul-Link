# /backend/app/logic/llm_client.py
import httpx
from backend.app.core.config import settings

async def call_groq(system_prompt: str, user_message: str, model: str = "llama-3.1-70b-versatile"):
    """
    Universal Groq Caller. Use 70b for the Actor and 8b for the smaller entities.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.8,
        "max_tokens": 1024
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"[Groq Error]: {str(e)}"