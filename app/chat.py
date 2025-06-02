from fastapi import Request, APIRouter
from app.ollama_client import ask_ollama
from app.short_term_memory import ShortTermMemory

router = APIRouter()
memory = ShortTermMemory()

@router.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        if not message:
            return {"error": "No se proporcionó ningún mensaje."}

        similar_context = memory.query(message)
        context_str = "\n".join(similar_context)
        enriched_prompt = f"Contexto previo:\n{context_str}\n\nPregunta:\n{message}"

        response = ask_ollama(enriched_prompt)
        print(f"[INFO] Respuesta generada: {response}")

        memory.add_interaction(message, response)
        print(f"[INFO] Guardado en memoria: Usuario: {message} | Asistente: {response}")

        return {"response": response}

    except Exception as e:
        print(f"[ERROR] Fallo en /chat: {str(e)}")
        return {"error": f"Error interno: {str(e)}"}
