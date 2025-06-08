import redis
import pickle
from typing import Optional, Dict, List
from memory_store_interface import MemoryStore  # Asegúrate de que MemoryStore esté importado desde el lugar adecuado

class RedisMemoryStore(MemoryStore):
    def __init__(self, host='localhost', port=6379):
        """
        Inicializa la conexión a Redis.

        Parámetros:
        - host: Dirección del servidor Redis (por defecto 'localhost').
        - port: Puerto del servidor Redis (por defecto 6379).
        """
        self.client = redis.StrictRedis(host=host, port=port, db=0)

    def add(self, id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """
        Almacena el contenido y los metadatos en Redis usando pickle.

        Parámetros:
        - id: Identificador único del documento.
        - content: El contenido del documento.
        - metadata: Metadatos adicionales opcionales.
        """
        data = {"content": content, "metadata": metadata}
        self.client.set(id, pickle.dumps(data))  # Serializa el diccionario con pickle

        # Agregar un índice en el campo "metadata" para búsquedas complejas por metadatos
        if metadata:
            for key, value in metadata.items():
                self.client.sadd(f"metadata:{key}:{value}", id)

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """
        Busca en los documentos almacenados en Redis usando el texto de consulta.
        También puede buscar en metadatos si es necesario.

        Parámetros:
        - query_text: Término de búsqueda dentro del contenido del documento.
        - n_results: Número de resultados a devolver (por defecto 5).

        Retorna:
        - Lista de resultados de contenido que coinciden con la búsqueda.
        """
        keys = self.client.keys(f"*{query_text}*")  # Buscar todas las claves que contengan el texto de la consulta
        results = []
        for key in keys:
            data = pickle.loads(self.client.get(key))
            if query_text in data['content']:
                results.append(data['content'])
                if len(results) >= n_results:
                    break
        return results

    def search_by_metadata(self, key: str, value: str) -> List[str]:
        """
        Realiza una búsqueda en los documentos basada en metadatos (por ejemplo, buscando todos los
        documentos que tengan un valor específico en un campo 'metadata').

        Parámetros:
        - key: El campo del metadato que estamos buscando (ej: "author").
        - value: El valor que debe tener ese campo de metadatos (ej: "Sebas").

        Retorna:
        - Lista de contenidos que coinciden con la búsqueda.
        """
        ids = self.client.smembers(f"metadata:{key}:{value}")
        return [pickle.loads(self.client.get(id))['content'] for id in ids]

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas sobre la memoria de Redis.

        Retorna:
        - Diccionario con el número total de entradas en Redis.
        """
        keys = self.client.keys('*')  # Obtiene todas las claves
        return {"total_entries": len(keys)}

    def clear(self) -> None:
        """
        Borra todos los documentos de Redis.
        """
        self.client.flushdb()  # Elimina todas las claves de la base de datos actual
