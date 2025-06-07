from chromadb.utils.embedding_functions import EmbeddingFunction
import os
import requests


class OpenAIEmbedding(EmbeddingFunction):
    def __init__(self, api_key=None):
        from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
        self.fn = OpenAIEmbeddingFunction(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def __call__(self, texts):
        return self.fn(texts)


class CohereEmbedding(EmbeddingFunction):
    def __init__(self, api_key=None):
        from chromadb.utils.embedding_functions import CohereEmbeddingFunction
        self.fn = CohereEmbeddingFunction(api_key=api_key or os.getenv("COHERE_API_KEY"))

    def __call__(self, texts):
        return self.fn(texts)


class OllamaEmbedding(EmbeddingFunction):
    """Generic Ollama embedding function using local model."""
    def __init__(self, model="mistral", host="http://localhost:11434"):
        self.model = model
        self.host = host

    def __call__(self, texts):
        if not isinstance(texts, list):
            texts = [texts]

        response = requests.post(
            f"{self.host}/api/embeddings",
            json={"model": self.model, "prompt": texts}
        )
        response.raise_for_status()
        return response.json()["embeddings"]


class DeepSeekEmbedding(EmbeddingFunction):
    def __init__(self, api_key=None, endpoint=None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.endpoint = endpoint or "https://api.deepseek.com/embeddings"

    def __call__(self, texts):
        if not isinstance(texts, list):
            texts = [texts]

        response = requests.post(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"input": texts}
        )
        response.raise_for_status()
        return [item["embedding"] for item in response.json()["data"]]


class MistralEmbedding(EmbeddingFunction):
    """For use with official mistral.ai API."""
    def __init__(self, api_key=None, endpoint=None, model="mistral-embed"):
        self.api_key = api_key or os.getenv("MISTRAL_APIKEY")
        self.endpoint = endpoint or "https://api.mistral.ai/v1/embeddings"
        self.model = model

    def __call__(self, texts):
        if not isinstance(texts, list):
            texts = [texts]

        response = requests.post(
            self.endpoint,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "input": texts
            }
        )
        response.raise_for_status()
        return [item["embedding"] for item in response.json()["data"]]

