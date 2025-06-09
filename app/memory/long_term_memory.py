from typing import List, Dict
from .store.chroma_memory_store import ChromaMemoryStore
from .store.memory_store_interface import MemoryStore
from .store.postgres_memory_store import PostgresMemoryStore
from .store.mongo_memory_store import MongoMemoryStore
from app.embeddings.embeddings import EmbeddingFunction
from app.llm_clients.llm_router import get_embedding_function
from scipy.spatial.distance import cosine


class LongTermMemory:
    def __init__(self):
        """
        Initialize different memory stores for long-term and short-term memory.
        """
        self.sources = {
            "chroma": ChromaMemoryStore(collection_name="long_term"),
            "postgres": PostgresMemoryStore(),
            "mongo": MongoMemoryStore(),
            # Add more memory sources as needed
        }
        # Function to embed text queries
        self.embedding_function = get_embedding_function()

    def decide_memory_source(self, query_text: str) -> MemoryStore:
        """
        Decide which memory source to use based on the type of query.
        We can enhance this by using an embedding model to determine the query type.
        """
        query_embedding = self.embedding_function(query_text)

        # If the query has semantic intent, prefer using Chroma (vector-based store)
        if self.is_semantic(query_text, query_embedding):
            return self.sources["chroma"]

        # Otherwise, default to a structured memory store like PostgreSQL or MongoDB
        return self.sources["postgres"]

    def is_semantic(self, query_text: str, query_embedding: List[float]) -> bool:
        """
        Use embedding-based logic to decide if a query is semantic or structured.
        Compares the query embedding to stored embeddings for similarity.
        """
        semantic_threshold = 0.8  # A threshold for cosine similarity to determine semantic queries

        # 1. Compare to recent session history embeddings (Faiss/Redis) for semantic relevance
        for recent_interaction in self.session_history:
            stored_embedding = recent_interaction['embedding']
            # Cosine similarity calculation
            similarity = 1 - cosine(query_embedding, stored_embedding)

            # 2. If the similarity is above the threshold, this is a semantic query related to session context
            if similarity > semantic_threshold:
                return True  # If the query is semantically similar to a recent interaction, it's a semantic query

        # 3. If the query is not similar to any recent history, classify as non-semantic (structured query)
        return False

    def add_interaction(self, user_message: str, assistant_response: str):
        """
        Store an interaction in the appropriate memory source (session or global).
        """
        memory_source = self.decide_memory_source(user_message)
        combined = f"User: {user_message}\nAssistant: {assistant_response}"
        doc_id = f"msg-{memory_source.get_stats().get('total_documents') + 1}"
        memory_source.add(doc_id, combined)

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """
        Query memory based on the type of query (semantic or structured).
        First try semantic search, then fallback to structured memory.
        """
        memory_source = self.decide_memory_source(query_text)

        # Perform semantic query using vector-based store if determined
        results = memory_source.query(query_text, n_results)

        # If no results are found, query in structured memory (PostgreSQL or MongoDB)
        if not results:
            if memory_source != self.sources["postgres"]:
                results = self.sources["postgres"].query(query_text, n_results)

        return results

    def get_stats(self) -> Dict:
        """
        Retrieve statistics for all memory stores (Chroma, PostgreSQL, MongoDB, etc.).
        """
        stats = {}
        for source_name, source in self.sources.items():
            stats[source_name] = source.get_stats()
        return stats

    def clear_all(self):
        """
        Clear all memory stores (for global and session memory).
        """
        for source_name, source in self.sources.items():
            source.clear()
