from pymongo import MongoClient
from typing import Optional, Dict, List
import os
from dotenv import load_dotenv
from .memory_store_interface import MemoryStore


class MongoMemoryStore(MemoryStore):
    def __init__(
        self,
        db_name: Optional[str] = None,
        collection_name: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Inicializa la conexión a MongoDB.
        """
        load_dotenv()

        db_name = db_name or os.getenv("MONGO_DB_NAME", "memory_db")
        collection_name = collection_name or os.getenv(
            "MONGO_COLLECTION_NAME", "documents")
        host = host or os.getenv("MONGO_HOST", "localhost")
        port = port or int(os.getenv("MONGO_PORT", 27017))
        username = username or os.getenv("MONGO_USERNAME")
        password = password or os.getenv("MONGO_PASSWORD")

        if username and password:
            uri = f"mongodb://{username}:{password}@{host}:{port}/"
            self.client = MongoClient(uri)
        else:
            self.client = MongoClient(f"mongodb://{host}:{port}/")

        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def add(self, id: str, content: str, metadata: Optional[Dict] = None) -> None:
        self.collection.insert_one({
            "id": id,
            "content": content,
            "metadata": metadata or {}
        })

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        cursor = self.collection.find(
            {"content": {"$regex": query_text, "$options": "i"}},
            {"_id": 0, "content": 1}
        ).limit(n_results)
        return [doc["content"] for doc in cursor]

    def get_stats(self) -> Dict:
        return {
            "collection": self.collection.name,
            "document_count": self.collection.count_documents({})
        }

    def clear(self) -> None:
        self.collection.delete_many({})
