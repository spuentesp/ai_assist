import psycopg2
from typing import Optional, Dict, List
import json
import os
from dotenv import load_dotenv
from .memory_store_interface import MemoryStore  # Suponiendo que MemoryStore está definido en memory/core.py

class PostgresMemoryStore(MemoryStore):
    def __init__(self, db_name: str = None, user: str = None, password: str = None, host: str = None, port: str = None):
        """
        Inicializa la conexión a la base de datos PostgreSQL.

        Parámetros:
        - db_name: Nombre de la base de datos.
        - user: Usuario de la base de datos.
        - password: Contraseña del usuario.
        - host: Dirección del host donde está la base de datos (por defecto 'localhost').
        - port: Puerto de conexión (por defecto '5432').
        """
        load_dotenv()
        db_name = db_name or os.getenv("POSTGRES_DB_NAME")
        user = user or os.getenv("POSTGRES_USER")
        password = password or os.getenv("POSTGRES_PASSWORD")
        host = host or os.getenv("POSTGRES_HOST", "localhost")
        port = port or os.getenv("POSTGRES_PORT", "5432")
        self.connection = psycopg2.connect(
            dbname=db_name, user=user, password=password, host=host, port=port
        )
        self.cursor = self.connection.cursor()

    def add(self, id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """
        Agrega un documento a la base de datos con un ID, contenido y metadatos opcionales.

        Parámetros:
        - id: Identificador único del documento.
        - content: El contenido del documento (texto).
        - metadata: Diccionario con información adicional del documento (opcional).
        """
        metadata_json = json.dumps(metadata) if metadata else None
        query = "INSERT INTO documents (id, content, metadata) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (id, content, metadata_json))
        self.connection.commit()

    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """
        Realiza una búsqueda en los documentos de la base de datos.

        Parámetros:
        - query_text: Texto de búsqueda dentro del contenido de los documentos.
        - n_results: Número de resultados a devolver (por defecto 5).

        Retorna:
        - Una lista con los contenidos de los documentos que coinciden con la búsqueda.
        """
        query = "SELECT content FROM documents WHERE content LIKE %s LIMIT %s"
        self.cursor.execute(query, (f"%{query_text}%", n_results))
        return [row[0] for row in self.cursor.fetchall()]

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas sobre la base de datos, como el número total de documentos.

        Retorna:
        - Un diccionario con estadísticas sobre la base de datos.
        """
        query = "SELECT count(*) FROM documents"
        self.cursor.execute(query)
        count = self.cursor.fetchone()[0]
        return {"total_documents": count}

    def clear(self) -> None:
        """
        Borra todos los documentos de la base de datos.
        """
        self.cursor.execute("DELETE FROM documents")
        self.connection.commit()

    def create_table(self):
        """
        Crea la tabla 'documents' si no existe.

        Esto incluye las columnas 'id', 'content' y 'metadata'.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                content TEXT,
                metadata JSONB
            );
        """)
        self.connection.commit()

    def update_metadata(self, id: str, new_metadata: Dict) -> None:
        """
        Actualiza los metadatos de un documento con un ID específico.

        Parámetros:
        - id: Identificador del documento a actualizar.
        - new_metadata: Nuevos metadatos para el documento.
        """
        metadata_json = json.dumps(new_metadata)
        self.cursor.execute("UPDATE documents SET metadata = %s WHERE id = %s", (metadata_json, id))
        self.connection.commit()

    def search_in_all_tables(self, search_term: str) -> List[str]:
        """
        Realiza una búsqueda en toda la base de datos (no solo en una tabla).

        Parámetros:
        - search_term: Texto para buscar en todos los documentos.

        Retorna:
        - Una lista con los contenidos de los documentos que coinciden con la búsqueda.
        """
        query = f"SELECT content FROM documents WHERE content LIKE %s"
        self.cursor.execute(query, (f"%{search_term}%",))
        return [row[0] for row in self.cursor.fetchall()]
