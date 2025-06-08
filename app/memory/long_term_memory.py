from typing import List, Dict, Optional

from .store.chroma_memory_store import ChromaMemoryStore
from .store.memory_store_interface import MemoryStore
from .store.postgres_memory_store import PostgresMemoryStore
from .store.mongo_memory_store import MongoMemoryStore
from app.embeddings.embeddings  import EmbeddingFunction
from app.llm_clients.llm_router import get_embedding_function

class LongTermMemory:
    def __init__(self):
        # Instanciar las diferentes fuentes de memoria
        self.sources = {
            "chroma": ChromaMemoryStore(path="chroma", collection_name="long_term"),
            "postgres": PostgresMemoryStore(),
            "mongo": MongoMemoryStore(),
            # Agregar más fuentes de memoria según sea necesario
        }

    def decide_memory_source(self, query_text: str) -> MemoryStore:
        """
        Decide qué fuente de memoria usar en función del tipo de consulta.
        Aquí podrías usar un heurístico basado en el contenido de la consulta.
        """
        # Ejemplo simple: Si la consulta parece ser semántica, usar la memoria vectorial
        if "busqueda semántica" in query_text:
            return self.sources["chroma"]
        else:
            return self.sources["postgres"]

    def add_interaction(self, user_message: str, assistant_response: str):
        """
        Almacena la interacción, decidiendo qué memoria usar para almacenarla.
        """
        memory_source = self.decide_memory_source(user_message)
        combined = f"Usuario: {user_message}\nAsistente: {assistant_response}"
        doc_id = f"msg-{memory_source.get_stats().get('total_documents') + 1}"
        memory_source.add(doc_id, combined)

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """
        Consulta la memoria para obtener resultados basados en la semántica.
        Si no encuentra en la memoria vectorial, consulta en la base de datos estructurada.
        """
        # Realizar búsqueda semántica
        memory_source = self.decide_memory_source(query_text)
        results = memory_source.query(query_text, n_results)
        
        # Si no se encuentran resultados, se puede buscar en la base de datos estructurada (ejemplo con PostgreSQL)
        if not results:
            if memory_source != self.sources["postgres"]:
                results = self.sources["postgres"].query(query_text, n_results)
        
        return results

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas de todas las fuentes de memoria.
        """
        stats = {}
        for source_name, source in self.sources.items():
            stats[source_name] = source.get_stats()
        return stats

    def clear_all(self):
        """
        Limpia todas las fuentes de memoria.
        """
        for source_name, source in self.sources.items():
            source.clear()
