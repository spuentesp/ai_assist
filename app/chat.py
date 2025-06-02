from fastapi import Request, APIRouter, Form
from app.ollama_client import ask_ollama
from app.short_term_memory import ShortTermMemory

router = APIRouter()
memory = ShortTermMemory()

@router.post("/chat")
async def chat(request: Request, message: str = Form(None)):
    try:
        if message is None:
            # JSON case
            data = await request.json()
            return await handle_json_request(data)
        else:
            # HTMX (form) case
            return await handle_htmx_request(message)
    except Exception as e:
        print(f"[ERROR] Fallo en /chat: {str(e)}")
        return handle_error_response(message, e)

async def handle_json_request(data):
    message = data.get("message")
    if not message:
        return {"error": "No se proporcionó ningún mensaje."}

    response = process_message(message)
    return {"response": response}

async def handle_htmx_request(message):
    response = process_message(message)
    return f"""
    <hr>
        <div class='message user'><strong>Usuario:</strong> {message}</div>
        <div class='message bot'><strong>Asistente:</strong> {response}</div>
    """

def process_message(message):
    similar_context = memory.query(message)
    context_str = "\n".join(similar_context)
    enriched_prompt = build_enriched_prompt(message, context_str)

    response = ask_ollama(enriched_prompt)
    memory.add_interaction(message, response)
    return response

def build_enriched_prompt(message, context_str):
    return f"Contexto previo:\n{context_str}\n\nPregunta:\n{message}"

def handle_error_response(message, error):
    if message is None:
        return {"error": f"Error interno: {str(error)}"}
    else:
        return f"<div class='message error'><strong>Error:</strong> {str(error)}</div>"
