import requests
from app.embeddings import OllamaEmbedding

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

def get_embedding_function(model: str = "mistral"):
    return OllamaEmbedding(model=model)

