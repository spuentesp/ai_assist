import os
import requests
from dotenv import load_dotenv
from app.embeddings.embeddings import MistralEmbedding
from .adapter_registry import register_adapter

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_APIKEY")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_APIKEY not set in environment.")

@register_adapter("mistral")
def ask(prompt, model="mistral-small"):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

@register_adapter("mistral")
def get_embedding_function(model: str = "mistral-small"):
    return MistralEmbedding(model=model, api_key=MISTRAL_API_KEY)
