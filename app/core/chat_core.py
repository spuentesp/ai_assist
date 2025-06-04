from app.memory.short_term_memory import ShortTermMemory
from app.memory.long_term_memory import LongTermMemory
from app.llm_clients.llm_router import ask_llm
from app.builders.prompt_builder import build_enriched_prompt

class ChatCore:
    def __init__(self):
        self.short_memory = ShortTermMemory()
        self.long_memory = LongTermMemory()

    def handle_message(self, message: str) -> str:
        if not message:
            raise ValueError("Mensaje vacío.")

        # Recuperar contexto
        short_context = self.short_memory.query(message)
        long_context = self.long_memory.query(message)

        # Preparar prompt enriquecido
        enriched_prompt = build_enriched_prompt(
            message,
            short_context_str="\n".join(short_context),
            long_context_str="\n".join(long_context)
        )

        # Enviar al modelo
        response = ask_llm(enriched_prompt)

        # Guardar en memoria
        self.short_memory.add_interaction(message, response)
        self.long_memory.add_interaction(message, response)

        return response
