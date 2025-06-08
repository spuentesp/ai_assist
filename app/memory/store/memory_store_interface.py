from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class MemoryStore(ABC):
    @abstractmethod
    def add(self, id: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Agrega un documento a la memoria"""
        pass

    @abstractmethod
    def query(self, query_text: str, n_results: int = 5) -> List[str]:
        """Consulta documentos relevantes dados un texto"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict:
        """Retorna estadísticas de la memoria"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Limpia toda la memoria"""
        pass
