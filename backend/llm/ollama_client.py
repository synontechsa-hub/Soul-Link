import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate(
    prompt: str,
    model: str = "llama3:8b",
    temperature: float = 0.8,
    max_tokens: int = 300,
) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["response"]
