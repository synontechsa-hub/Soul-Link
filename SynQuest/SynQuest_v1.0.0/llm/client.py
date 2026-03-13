import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# We'll initialize the client lazily so it doesn't crash on import if no key
_client = None

def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")
        _client = OpenAI(api_key=api_key)
    return _client

def generate_narration(system_message: str, history: list[dict], new_prompt: str) -> str:
    """
    Sends the strict system context, conversation history, and the new mechanical prompt to the LLM.
    Returns the narrative string.
    """
    client = get_client()
    
    messages = [{"role": "system", "content": system_message}]
    messages.extend(history)
    messages.append({"role": "user", "content": new_prompt})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Cheap, fast, smart enough for MUDs
            messages=messages,
            temperature=0.7,
            max_tokens=250
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[SYSTEM ERROR: Narrator failed - {str(e)}]"
