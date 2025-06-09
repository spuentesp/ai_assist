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
        Initializes a connection to the Chroma v1 server and retrieves
        the specified collection. Embedding is handled externally.
        """
        host = host or os.getenv("CHROMA_HOST", "localhost")
        port = port or int(os.getenv("CHROMA_PORT", "8000"))
        self.collection_name = collection_name

        # Conexión al nuevo cliente REST v1
        self.client = HttpClient(host=host, port=port)

        # Embedding externo
        self.embedding_fn = get_embedding_function()

        # Crea o recupera la colección
        self.collection = self.client.get_or_create_collection(
            self.collection_name)

    def add(self, id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """
        Adds a new document to the collection using external embeddings.
        """
        embedding = self.embedding_fn([content])[0]  # embed como lista
        self.collection.add(
            documents=[content],
            ids=[id],
            metadatas=[metadata or {}],
            embeddings=[embedding]
        )

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """
        Performs a similarity search using external embedding function.
        """
        embedding = self.embedding_fn([query_text])[0]
        results = self.collection.query(
            query_embeddings=[embedding], n_results=n_results
        )
        return results.get("documents", [[]])[0]

    def get_stats(self) -> Dict:
        """
        Returns basic statistics about the collection.
        """
        return {
            "collection": self.collection.name,
            "document_count": self.collection.count()
        }

    def clear(self) -> None:
        """
        Deletes and recreates the collection.
        """
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            self.collection_name)
