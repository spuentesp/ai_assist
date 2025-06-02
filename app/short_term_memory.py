import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer

class ShortTermMemory:
    def __init__(self, dim=384, max_items=100, snapshot_path="./memory_snapshot"):
        self.dim = dim
        self.max_items = max_items
        self.snapshot_path = snapshot_path
        self.index_file = os.path.join(snapshot_path, "index.faiss")
        self.texts_file = os.path.join(snapshot_path, "texts.npy")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        os.makedirs(snapshot_path, exist_ok=True)
        self.texts = []
        self.index = faiss.IndexFlatL2(dim)

        self.load()

    def add_interaction(self, user_message, assistant_response):
        combined = f"Usuario: {user_message}\nAsistente: {assistant_response}"
        embedding = self._embed(combined)

        if len(self.texts) >= self.max_items:
            self.texts.pop(0)
            embeddings = np.array([self._embed(t) for t in self.texts])
            self.index = faiss.IndexFlatL2(self.dim)
            self.index.add(embeddings)

        self.index.add(np.array([embedding]))
        self.texts.append(combined)

    def query(self, text, top_k=3):
        if len(self.texts) == 0:
            return []

        embedding = self._embed(text)
        D, I = self.index.search(np.array([embedding]), top_k)
        results = [self.texts[i] for i in I[0] if i < len(self.texts)]
        return results

    def save(self):
        faiss.write_index(self.index, self.index_file)
        np.save(self.texts_file, np.array(self.texts))
        print("[INFO] Memoria guardada a snapshot.")

    def load(self):
        if os.path.exists(self.index_file) and os.path.exists(self.texts_file):
            self.index = faiss.read_index(self.index_file)
            self.texts = np.load(self.texts_file).tolist()
            print("[INFO] Memoria cargada desde snapshot.")
        else:
            print("[INFO] No se encontró snapshot previo, iniciando vacío.")

    def _embed(self, text):
        return self.model.encode(text)
