import requests
from app.embeddings.embeddings import OllamaEmbedding
from .adapter_registry import register_adapter

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"

@register_adapter("ollama")
def ask(prompt: str, model: str = "mistral") -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload, timeout=10)
    response.raise_for_status()
    return response.json().get("response", "")

@register_adapter("ollama")
def get_embedding_function(model: str = "mistral"):
    return OllamaEmbedding(model=model)
