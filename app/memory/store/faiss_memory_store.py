import faiss
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import numpy as np
from memory_store_interface import MemoryStore

class FaissMemoryStore(MemoryStore):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = faiss.IndexFlatL2(self.model.get_sentence_embedding_dimension())
        self.texts = []
        self.metadata_list = []

    def add(self, id: str, content: str, metadata: Optional[Dict] = None) -> None:
        embedding = self.model.encode([content])[0].astype("float32")
        self.index.add(np.array([embedding]))
        self.texts.append(content)
        self.metadata_list.append(metadata or {})

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        if len(self.texts) == 0:
            return []

        query_vec = self.model.encode([query_text])[0].astype("float32").reshape(1, -1)
        D, I = self.index.search(query_vec, min(n_results, len(self.texts)))
        return [self.texts[i] for i in I[0]]

    def get_stats(self) -> Dict:
        return {
            "total_items": len(self.texts),
            "index_type": "FAISS (L2)",
        }

    def clear(self) -> None:
        dim = self.index.d
        self.index = faiss.IndexFlatL2(dim)
        self.texts.clear()
        self.metadata_list.clear()
