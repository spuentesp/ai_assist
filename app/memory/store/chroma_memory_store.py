from chromadb import HttpClient
from app.llm_clients.llm_router import get_embedding_function
from .memory_store_interface import MemoryStore
from typing import List, Dict, Optional
import os


class ChromaMemoryStore(MemoryStore):
    def __init__(
        self,
        host: str = None,
        port: int = None,
        collection_name: str = "long_term"
    ):
        """
        Initializes a connection to the ChromaDB server and creates or retrieves
        the specified collection with an embedding function.
        """
        host = host or os.getenv("CHROMA_HOST", "localhost")
        port = port or int(os.getenv("CHROMA_PORT", "8001"))
        self.collection_name = collection_name

        self.client = HttpClient(host=host, port=port)
        self.embedding_fn = get_embedding_function()
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )

    def add(self, id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """
        Adds a new document to the collection.
        """
        self.collection.add(
            documents=[content],
            ids=[id],
            metadatas=[metadata or {}]
        )

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """
        Performs a similarity search on the collection.
        Returns a list of the most similar documents.
        """
        results = self.collection.query(
            query_texts=[query_text], n_results=n_results)
        return results.get("documents", [[]])[0]

    def get_stats(self) -> Dict:
        """
        Returns statistics about the current collection.
        """
        return {
            "collection": self.collection.name,
            "document_count": self.collection.count()
        }

    def clear(self) -> None:
        """
        Deletes and recreates the collection.
        Useful for resetting memory.
        """
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )
