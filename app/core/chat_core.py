from app.memory.short_term_memory import ShortTermMemory
from app.core.chroma_core import ChromaCore
from app.llm_clients.llm_router import ask_llm
from app.builders.prompt_builder import build_enriched_prompt

class ChatCore:
    def __init__(self):
        self.short_memory = ShortTermMemory()
        self.long_memory = ChromaCore(
            collection_name="chat_memory",
            embedding_model="ollama",  # o "deepseek"
            model_config={"model": "mistral"}  # configuraciones específicas del modelo
        )

    def handle_message(self, message: str) -> str:
        if not message:
            raise ValueError("Mensaje vacío.")

        # Recuperar contexto corto
        short_context = self.short_memory.query(message)

        # Recuperar contexto largo de ChromaDB
        long_context_results = self.long_memory.query(message)
        long_context = [res for res in long_context_results.get("documents", [[]])[0]]

        # Construir prompt
        enriched_prompt = build_enriched_prompt(
            message,
            short_context_str="\n".join(short_context),
            long_context_str="\n".join(long_context)
        )

        # Consultar LLM
        response = ask_llm(enriched_prompt)

        # Guardar interacciones
        self.short_memory.add_interaction(message, response)
        self.long_memory.add_document(doc_id=message[:48], content=f"{message}\n{response}")

        return response
