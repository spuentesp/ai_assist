from app.memory.memory_orchestrator import MemoryOrchestrator
from app.llm_clients.llm_orchestrator import LLMOrchestrator
from app.utils.utils import render_template


class ChatCore:
    """
    Core class responsible for handling chat interactions between the user and the system.
    It retrieves memory context, constructs prompts, invokes the LLM orchestrator, and stores interactions.
    """
    def __init__(self):
        """
        Initializes the ChatCore with:
        - A memory orchestrator that routes queries to long- and short-term memory.
        - A smart LLM orchestrator for parallel model selection and meta-ranking.
        """
        self.memory_orchestrator = MemoryOrchestrator()
        self.llm_orchestrator = LLMOrchestrator()

    def handle_message(self, message: str) -> str:
        """
        Handles a user message by:
        1. Retrieving context from short- and long-term memory.
        2. Constructing a context-enriched prompt.
        3. Sending the prompt to the LLM orchestrator.
        4. Storing the message and response in memory.

        Args:
            message (str): User's input message.

        Returns:
            str: Generated response from the LLM orchestrator.
        """
        if not message:
            raise ValueError("Mensaje vacío.")

        # Step 1: Retrieve relevant memory context
        memory_context = self.memory_orchestrator.query(message)

        # Step 2: Build the enriched prompt
        enriched_prompt = render_template(
                            "enriched_prompt.j2",
                            {
                                "short_context": "",  # Add short context if needed
                                "long_context": "\n".join(memory_context),
                                "question": message
                            }
                        )

        # Step 3: Use LLM orchestrator to generate a response
        response = self.llm_orchestrator.ask(enriched_prompt)

        # Step 4: Store the interaction in memory
        self.memory_orchestrator.update_memory(message, response)

        return response
