import os
import requests
from app.embeddings import DeepSeekEmbedding

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def ask_deepseek(prompt, model="deepseek-chat"):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
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

def get_embedding_function(model: str = "deepseek-chat"):
    return DeepSeekEmbedding(api_key=DEEPSEEK_API_KEY)
