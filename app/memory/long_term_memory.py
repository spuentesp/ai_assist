import chromadb
from sentence_transformers import SentenceTransformer

class LongTermMemory:
    def __init__(self, persist_directory="./chroma_memory"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection("memory")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def add(self, id, text, metadata=None):
        embedding = self.model.encode([text])[0]
        self.collection.add(
            ids=[id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}]
        )
    
    def add_interaction(self, user_message, assistant_response):
        combined = f"Usuario: {user_message}\nAsistente: {assistant_response}"
        embedding = self.model.encode([combined])[0]
        self.collection.add(
            ids=[str(len(self.collection.get()['ids']) + 1)],
            embeddings=[embedding],
            documents=[combined],
            metadatas={}
        )

    def query(self, text, n_results=3):
        embedding = self.model.encode([text])[0]
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )
        return results
