from app.core.chroma_core import ChromaCore
from app.llm_clients.llm_router import get_embedding_model_and_config

class LongTermMemory:
    def __init__(self):
        model_key, model_config = get_embedding_model_and_config()

        self.sources = {
                "chroma": ChromaCore(
        collection_name="long_memory",
        embedding_model=model_key,
        model_config=model_config
    ),
            # en el futuro:
            # "doc_db": DocumentDBClient(),
            # "sql": SQLMemoryClient(),
            # "faiss": FAISSMemory(path, embedding_fn),
        }

    def add_interaction(self, user_message: str, assistant_response: str):
        combined = f"Usuario: {user_message}\nAsistente: {assistant_response}"
        doc_id = f"msg-{self.sources['chroma'].collection.count() + 1}"
        self.sources["chroma"].add_document(doc_id, combined)
        # Aquí podrías agregar otras fuentes si quisieras persistir en múltiples lugares

    def query(self, message: str, n_results: int = 5) -> list[str]:
        results = []

        chroma_results = self.sources["chroma"].query(message, n_results=n_results)
        results.extend(chroma_results.get("documents", [[]])[0])

        # futuro:
        # doc_results = self.sources["doc_db"].query(...)
        # results.extend(doc_results)

        return results

    def get_stats(self):
        return {
            "chroma": self.sources["chroma"].get_stats(),
            # "doc_db": self.sources["doc_db"].get_stats(),
        }

    def clear_all(self):
        self.sources["chroma"].clear_all()
        # self.sources["doc_db"].clear_all()
