import requests
import logging

# ─────────────────────────────────────────────
# 🤖 LLM CONFIGURATION (OLLAMA)
# ─────────────────────────────────────────────

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3:8b"

logging.basicConfig(level=logging.INFO)

# ─────────────────────────────────────────────
# 🧠 LLM RESPONSE GENERATION
# ─────────────────────────────────────────────
#
# Sends a fully constructed prompt to the Ollama API
# and returns the model's response as plain text.
#
# This function is intentionally simple and blocking:
# - No streaming
# - One prompt → one reply
# - Easy to debug and replace later

def generate_reply(prompt: str) -> str:
    """
    Sends a prompt to Ollama and returns the model's reply.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )
        response.raise_for_status()

        data = response.json()
        return data.get("response", "").strip()

    except Exception as e:
        logging.error(f"Ollama error: {e}")
        return "⚠️ Error: LLM unavailable."
