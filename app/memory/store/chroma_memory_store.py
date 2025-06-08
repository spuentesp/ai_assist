from chromadb import PersistentClient
from app.llm_clients.llm_router import get_embedding_function
from .memory_store_interface import MemoryStore
from typing import List, Dict, Optional
import os


class ChromaMemoryStore(MemoryStore):
    def __init__(self, path: str = "chroma", collection_name: str = "long_term"):
        # Ensure the directory exists
        os.makedirs(path, exist_ok=True)
        self.client = PersistentClient(path=path)
        self.embedding_fn = get_embedding_function()
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def add(self, id: str, content: str, metadata: Optional[Dict] = None) -> None:
        self.collection.add(
            documents=[content],
            ids=[id],
            metadatas=[metadata or {}]
        )

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        results = self.collection.query(query_texts=[query_text], n_results=n_results)
        return results.get("documents", [[]])[0]

    def get_stats(self) -> Dict:
        return {
            "collection": self.collection.name,
            "document_count": self.collection.count()
        }

    def clear(self) -> None:
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection.name,
            embedding_function=self.embedding_fn
        )
