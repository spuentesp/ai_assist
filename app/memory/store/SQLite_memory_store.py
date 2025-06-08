import sqlite3
import json
from typing import Optional, Dict, List
from memory_store_interface import MemoryStore  # Asegúrate de que MemoryStore esté importado desde el lugar adecuado

class SQLiteMemoryStore(MemoryStore):
    def __init__(self):
        """
        Inicializa la base de datos SQLite en memoria.
        """
        self.connection = sqlite3.connect(':memory:')  # Crea una base de datos SQLite en memoria
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS metadata (id TEXT PRIMARY KEY, metadata TEXT)''')

    def add(self, db_name: str, id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """
        Agrega un documento y metadatos a la base de datos SQLite.
        Si no existe la base de datos, la crea automáticamente.

        Parámetros:
        - db_name: Nombre de la base de datos que contiene el documento.
        - id: Identificador único del documento.
        - content: El contenido del documento.
        - metadata: Metadatos adicionales opcionales, que se almacenan como JSON.
        """
        self.create_db(db_name)
        metadata_json = json.dumps(metadata) if metadata else None
        table_name = f"documents_{db_name}"
        self.cursor.execute(f"INSERT OR REPLACE INTO {table_name} (id, content, metadata) VALUES (?, ?, ?)", (id, content, metadata_json))
        self.connection.commit()

    def query(self, db_name: str, query_text: str, n_results: int = 5) -> List[str]:
        """
        Realiza una búsqueda en los documentos de SQLite en memoria dentro de la base de datos especificada.

        Parámetros:
        - db_name: El nombre de la base de datos que se va a consultar.
        - query_text: Término de búsqueda dentro del contenido de los documentos.
        - n_results: Número de resultados a devolver (por defecto 5).

        Retorna:
        - Lista de contenidos que coinciden con la búsqueda.
        """
        table_name = f"documents_{db_name}"
        self.cursor.execute(f"SELECT content FROM {table_name} WHERE content LIKE ? LIMIT ?", ('%' + query_text + '%', n_results))
        return [row[0] for row in self.cursor.fetchall()]

    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas sobre las bases de datos y documentos creados.

        Retorna:
        - Diccionario con el número total de bases de datos y documentos.
        """
        self.cursor.execute("SELECT count(*) FROM metadata")
        return {"total_databases": self.cursor.fetchone()[0]}

    def clear(self) -> None:
        """
        Borra todos los documentos de todas las bases de datos.
        """
        self.cursor.execute("DELETE FROM metadata")
        self.connection.commit()

    def create_db(self, db_name: str) -> None:
        """
        Crea una nueva base de datos y tabla de documentos si no existe.
        Además, crea una tabla de metadatos asociada a la base de datos.

        Parámetros:
        - db_name: El nombre de la base de datos que se va a crear.
        """
        table_name = f"documents_{db_name}"
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id TEXT PRIMARY KEY, content TEXT, metadata TEXT)")
        self.cursor.execute("INSERT OR REPLACE INTO metadata (id, metadata) VALUES (?, ?)", (db_name, f"Metadata for {db_name}"))
        self.connection.commit()

    def create_metadata_table(self, db_name: str) -> None:
        """
        Crea una tabla de metadatos para el seguimiento de las bases de datos creadas.

        Parámetros:
        - db_name: El nombre de la base de datos que se está creando.
        """
        self.cursor.execute("CREATE TABLE IF NOT EXISTS metadata (db_name TEXT PRIMARY KEY, creation_info TEXT)")
        self.cursor.execute("INSERT OR REPLACE INTO metadata (db_name, creation_info) VALUES (?, ?)", (db_name, f"Created on {db_name}"))
        self.connection.commit()
