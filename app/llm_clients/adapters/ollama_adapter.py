import requests
import logging
from app.embeddings.embeddings import OllamaEmbedding
from .adapter_registry import register_adapter

# Set up the Ollama API URL
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"

# Configure logging
logging.basicConfig(level=logging.INFO)

@register_adapter("ollama")
def ask(prompt: str, model: str = "mistral") -> str:
    """
    Ask the Ollama model for a response based on the prompt.
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        # Make a POST request to Ollama API
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()  # Will raise an HTTPError if the response code is 4xx/5xx
        return response.json().get("response", "")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred while asking Ollama model: {http_err}")
        raise
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error occurred while asking Ollama model: {req_err}")
        raise

@register_adapter("ollama")
def get_embedding_function(model: str = "mistral"):
    """
    Get the embedding function for the Ollama model.
    """
    try:
        return OllamaEmbedding(model=model)
    except Exception as e:
        logging.error(f"Error occurred while getting embedding function for {model}: {e}")
        raise
