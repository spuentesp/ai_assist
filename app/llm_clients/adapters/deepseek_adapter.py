import os
import requests
from dotenv import load_dotenv
import logging
from app.embeddings.embeddings import DeepSeekEmbedding
from .adapter_registry import register_adapter

# Load environment variables
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_APIKEY")

# Set up logging
logging.basicConfig(level=logging.INFO)

@register_adapter("deepseek")
def ask(prompt, model="deepseek-chat"):
    """
    Ask the DeepSeek model for a response based on the prompt.
    """
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

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()  # Will raise an HTTPError if the response code is 4xx/5xx
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred while asking DeepSeek model: {http_err}")
        raise
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error occurred while asking DeepSeek model: {req_err}")
        raise

@register_adapter("deepseek")
def get_embedding_function(model: str = "deepseek-chat"):
    """
    Get the embedding function for the DeepSeek model.
    """
    try:
        return DeepSeekEmbedding(model=model, api_key=DEEPSEEK_API_KEY)
    except Exception as e:
        logging.error(f"Error occurred while getting embedding function for {model}: {e}")
        raise
