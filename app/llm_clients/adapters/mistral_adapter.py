import os
import requests
from dotenv import load_dotenv
import logging
from app.embeddings.embeddings import MistralEmbedding
from .adapter_registry import register_adapter

# Load environment variables
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_APIKEY")

# Set up logging
logging.basicConfig(level=logging.INFO)

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_APIKEY not set in environment.")

@register_adapter("mistral")
def ask(prompt, model="mistral-small"):
    """
    Ask the Mistral model for a response based on the prompt.
    """
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

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()  # Will raise an HTTPError if the response code is 4xx/5xx
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred while asking Mistral model: {http_err}")
        raise
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error occurred while asking Mistral model: {req_err}")
        raise

@register_adapter("mistral")
def get_embedding_function(model: str = "mistral-small"):
    """
    Get the embedding function for the Mistral model.
    """
    try:
        return MistralEmbedding(model=model, api_key=MISTRAL_API_KEY)
    except Exception as e:
        logging.error(f"Error occurred while getting embedding function for {model}: {e}")
        raise

