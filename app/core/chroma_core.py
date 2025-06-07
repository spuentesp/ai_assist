import os
from chromadb import PersistentClient
from app.embeddings.embeddings import (
    OpenAIEmbedding,
    CohereEmbedding,
    OllamaEmbedding,
    DeepSeekEmbedding
)

class ChromaCore:
    def __init__(self, collection_name="main", embedding_model="ollama", model_config=None):
        self.client = PersistentClient()
        self.embedding_fn = self._load_embedding_function(embedding_model, model_config or {})
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def _load_embedding_function(self, embedding_model, config):
        if embedding_model == "openai":
            return OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY"))
        elif embedding_model == "cohere":
            return CohereEmbedding(api_key=os.getenv("COHERE_API_KEY"))
        elif embedding_model == "ollama":
            return OllamaEmbedding(model=config.get("model", "mistral"))
        elif embedding_model == "deepseek":
            return DeepSeekEmbedding(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                endpoint=config.get("endpoint", "https://api.deepseek.com/embeddings")
            )
        else:
            raise ValueError(f"Embedding model '{embedding_model}' no soportado")

    def add_document(self, doc_id: str, content: str, metadata: dict = None):
        self.collection.add(
            documents=[content],
            ids=[doc_id],
            metadatas=[metadata or {}]
        )

    def query(self, query_text: str, n_results: int = 5):
        return self.collection.query(query_texts=[query_text], n_results=n_results)

    def delete_document(self, doc_id: str):
        self.collection.delete(ids=[doc_id])

    def get_stats(self):
        return {
            "name": self.collection.name,
            "count": self.collection.count()
        }

    def clear_all(self):
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            embedding_function=self.embedding_fn
        )
