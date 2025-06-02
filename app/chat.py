from fastapi import Request, APIRouter, Form
from fastapi.responses import JSONResponse, HTMLResponse

from app.ollama_client import ask_ollama
from app.short_term_memory import ShortTermMemory
from app.long_term_memory import LongTermMemory

router = APIRouter()
short_memory = ShortTermMemory()
long_memory = LongTermMemory()


@router.post("/chat")
async def chat(request: Request, message: str = Form(None)):
    try:
        if message is not None:
            return await handle_htmx_request(message)
        else:
            data = await request.json()
            return await handle_json_request(data)
    except Exception as e:
        print(f"[ERROR] Fallo en /chat: {str(e)}")
        return handle_error_response(e, is_htmx=(message is not None))


# --- Processors ---

async def handle_json_request(data):
    message = extract_message(data)
    response = process_message(message)
    return JSONResponse(content={"response": response})


async def handle_htmx_request(message):
    response = process_message(message)
    html_fragment = build_htmx_response(message, response)
    return HTMLResponse(content=html_fragment)


def process_message(message):
    if not message:
        raise ValueError("No se proporcionó ningún mensaje.")

    # Recuperar contexto corto
    short_context = short_memory.query(message)
    short_context_str = "\n".join(short_context)

    # Recuperar contexto largo
    long_context = long_memory.query(message)
    long_context_str = "\n".join(long_context)

    # Combinar
    enriched_prompt = build_enriched_prompt(message, short_context_str, long_context_str)

    response = ask_ollama(enriched_prompt)

    # Guardar en ambas memorias
    short_memory.add_interaction(message, response)
    long_memory.add_interaction(message, response)

    return response


# --- Builders ---

def extract_message(data):
    return data.get("message")


def build_enriched_prompt(message, short_context_str, long_context_str):
    return f"""Contexto corto plazo:
{short_context_str}

Contexto largo plazo:
{long_context_str}

Pregunta:
{message}
"""


def build_htmx_response(message, response):
    return f"""
    <hr>
    <div class='message user'><strong>Usuario:</strong> {message}</div>
    <div class='message bot'><strong>Asistente:</strong> {response}</div>
    """


def handle_error_response(error, is_htmx=False):
    error_msg = f"Error interno: {str(error)}"
    if is_htmx:
        return HTMLResponse(content=f"<div class='message error'><strong>Error:</strong> {error_msg}</div>")
    else:
        return JSONResponse(content={"error": error_msg}, status_code=500)
