from pymongo import MongoClient
from typing import Optional, Dict, List
import json
import os
from dotenv import load_dotenv
# Importamos MemoryStore desde otro archivo
from .memory_store_interface import MemoryStore  # Asegúrate de que la ruta sea correcta

class MongoMemoryStore(MemoryStore):
    def __init__(self, db_name: str = None, collection_name: str = None, host: str = None, port: int = None):
        """
        Inicializa la conexión a la base de datos MongoDB.

        Parámetros:
        - db_name: Nombre de la base de datos.
        - collection_name: Nombre de la colección dentro de la base de datos.
        - host: Dirección del host donde está la base de datos (por defecto 'localhost').
        - port: Puerto de conexión (por defecto 27017).
        """
        load_dotenv()
        db_name = db_name or os.getenv("MONGO_DB_NAME")
        collection_name = collection_name or os.getenv("MONGO_COLLECTION_NAME")
        host = host or os.getenv("MONGO_HOST", "localhost")
        port = port or int(os.getenv("MONGO_PORT", 27017))
        self.client = MongoClient(host, port)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def add(self, id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """
        Agrega un documento a la colección de MongoDB con un ID, contenido y metadatos opcionales.

        Parámetros:
        - id: Identificador único del documento.
        - content: El contenido del documento (texto).
        - metadata: Diccionario con información adicional del documento (opcional).
        """
        document = {
            "id": id,
            "content": content,
            "metadata": metadata if metadata else {}
        }
        self.collection.insert_one(document)

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """
        Realiza una búsqueda en los documentos de la colección MongoDB.

        Parámetros:
        - query_text: Texto de búsqueda dentro del contenido de los documentos.
        - n_results: Número de resultados a devolver (por defecto 5).

        Retorna:
        - Una lista con los contenidos de los documentos que coinciden con la búsqueda.
        """
        results = self.collection.find({"content": {"$regex": query_text}}, {"content": 1}).limit(n_results)
        return [result['content'] for result in results]

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas sobre la colección, como el número total de documentos.

        Retorna:
        - Un diccionario con estadísticas sobre la colección.
        """
        count = self.collection.count_documents({})
        return {"total_documents": count}

    def clear(self) -> None:
        """
        Borra todos los documentos de la colección MongoDB.
        """
        self.collection.delete_many({})

    def create_collection(self):
        """
        Crea la colección 'documents' si no existe.
        """
        if self.collection.name not in self.db.list_collection_names():
            self.db.create_collection(self.collection.name)

    def search_in_all_documents(self, search_term: str) -> List[str]:
        """
        Realiza una búsqueda en todos los documentos de la colección.

        Parámetros:
        - search_term: Texto para buscar en todos los documentos.

        Retorna:
        - Una lista con los contenidos de los documentos que coinciden con la búsqueda.
        """
        results = self.collection.find({"content": {"$regex": search_term}})
        return [result['content'] for result in results]

    def update_document_metadata(self, id: str, new_metadata: Dict) -> None:
        """
        Actualiza los metadatos de un documento con un ID específico en MongoDB.

        Parámetros:
        - id: Identificador del documento a actualizar.
        - new_metadata: Nuevos metadatos para el documento.
        """
        self.collection.update_one({"id": id}, {"$set": {"metadata": new_metadata}})
