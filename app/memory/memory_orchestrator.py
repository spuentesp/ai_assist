from typing import List, Dict
from app.embeddings.embeddings import EmbeddingFunction
from app.llm_clients.llm_router import get_embedding_function
from app.memory.short_term_memory import ShortTermMemory
from app.memory.long_term_memory import LongTermMemory
from scipy.spatial.distance import cosine

class MemoryOrchestrator:
    def __init__(self):
        self.short_term_memory = ShortTermMemory()
        self.long_term_memory = LongTermMemory()
        self.embedding_function = get_embedding_function()
        self.session_history = []

    def is_semantic(self, query_text: str) -> bool:
        embedding = self.embedding_function(query_text)
        for interaction in self.session_history:
            sim = 1 - cosine(embedding, interaction['embedding'])
            if sim > 0.8:
                return True
        return False

    def query(self, query_text: str, top_k: int = 5) -> List[str]:
        embedding = self.embedding_function(query_text)
        is_sem = self.is_semantic(query_text)

        if is_sem:
            return self.short_term_memory.query(query_text, top_k)
        else:
            return self.long_term_memory.query(query_text, top_k)

    def add_interaction(self, user_message: str, assistant_response: str):
        embedding = self.embedding_function(user_message)
        is_sem = self.is_semantic(user_message)

        if is_sem:
            self.short_term_memory.add_interaction(user_message, assistant_response)
        else:
            self.long_term_memory.add_interaction(user_message, assistant_response)

        self.session_history.append({
            "message": user_message,
            "embedding": embedding,
            "assistant_response": assistant_response
        })

    def clear_short_term(self):
        self.short_term_memory.clear_all()

    def clear_all(self):
        self.short_term_memory.clear_all()
        self.long_term_memory.clear_all()

    def get_stats(self) -> Dict[str, Dict]:
        return {
            "short_term": self.short_term_memory.get_stats(),
            "long_term": self.long_term_memory.get_stats()
        }
