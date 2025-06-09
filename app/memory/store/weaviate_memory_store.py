import os
import logging
import atexit
from typing import List, Dict, Optional

import weaviate
from dotenv import load_dotenv
from app.llm_clients.llm_router import get_embedding_function
from .memory_store_interface import MemoryStore

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)


class WeaviateMemoryStore(MemoryStore):
    def __init__(
        self,
        context_name: str = "default_context",
        host: str = None,
        port: str = None,
    ):
        """
        Inicializa la conexión con Weaviate y asegura la existencia de la clase para el contexto.
        """
        host = host or os.getenv("WEAVIATE_HOST", "localhost")
        port = port or os.getenv("WEAVIATE_PORT", "8080")
        self.class_name = self._format_class_name(context_name)
        self.embedding_fn = get_embedding_function()
        self.client = weaviate.Client(url=f"http://{host}:{port}")

        self._ensure_class_exists()

    def _format_class_name(self, name: str) -> str:
        """
        Formatea un nombre válido de clase para Weaviate.
        """
        clean = ''.join(c if c.isalnum() else '_' for c in name)
        return clean[:1].upper() + clean[1:]

    def _ensure_class_exists(self):
        """
        Verifica si la clase existe en el esquema y la crea si es necesario.
        """
        try:
            schema = self.client.schema.get()
            existing_classes = [c.get("class")
                                for c in schema.get("classes", [])]
            if self.class_name not in existing_classes:
                self._create_class()
        except Exception as e:
            logger.warning(f"No se pudo verificar el esquema en Weaviate: {e}")

    def _create_class(self):
        """
        Crea la clase en Weaviate si no existe.
        """
        schema = {
            "class": self.class_name,
            "vectorizer": "none",
            "properties": [
                {"name": "content", "dataType": ["text"]},
                {"name": "metadata", "dataType": ["text"]}
            ]
        }
        try:
            self.client.schema.create_class(schema)
            logger.info(
                f"Clase '{self.class_name}' creada exitosamente en Weaviate.")
        except weaviate.exceptions.UnexpectedStatusCodeException as e:
            if "already exists" in str(e):
                logger.info(f"La clase '{self.class_name}' ya existe.")
            else:
                logger.error(
                    f"No se pudo crear la clase '{self.class_name}': {e}")

    def add(self, id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """
        Agrega un objeto con embedding a Weaviate.
        """
        try:
            vector = self.embedding_fn(content)
            obj = {
                "content": content,
                "metadata": str(metadata or {})
            }
            self.client.data_object.create(
                data_object=obj,
                class_name=self.class_name,
                uuid=id,
                vector=vector
            )
        except Exception as e:
            logger.error(f"No se pudo agregar el objeto a Weaviate: {e}")

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """
        Realiza una búsqueda por similitud vectorial.
        """
        try:
            vector = self.embedding_fn(query_text)
            result = self.client.query.get(
                self.class_name,
                ["content"]
            ).with_vector(vector).with_limit(n_results).do()

            return [
                item["content"]
                for item in result.get("data", {}).get("Get", {}).get(self.class_name, [])
            ]
        except Exception as e:
            logger.error(f"Error al consultar Weaviate: {e}")
            return []

    def get_stats(self) -> Dict:
        """
        Devuelve estadísticas sobre los objetos almacenados.
        """
        try:
            agg = self.client.query.aggregate(
                self.class_name).with_meta_count().do()
            count = agg["data"]["Aggregate"][self.class_name][0]["meta"]["count"]
        except Exception as e:
            logger.warning(f"No se pudo obtener estadísticas de Weaviate: {e}")
            count = 0
        return {
            "class": self.class_name,
            "object_count": count
        }

    def clear(self) -> None:
        """
        Borra todos los objetos dentro de la clase.
        """
        try:
            self.client.batch.delete_objects(
                class_name=self.class_name,
                where={"operator": "IsNotNull", "path": ["content"]}
            )
            logger.info(
                f"Se eliminaron todos los objetos de la clase '{self.class_name}'.")
        except Exception as e:
            logger.error(
                f"No se pudieron borrar los objetos de la clase '{self.class_name}': {e}")
