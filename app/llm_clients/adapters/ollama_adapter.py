import requests

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"

def ask_ollama(prompt: str, model: str = "mistral") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=10)
    response.raise_for_status()
    return response.json().get("response", "")
