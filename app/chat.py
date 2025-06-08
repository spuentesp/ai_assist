from fastapi import Request, APIRouter, Form
from fastapi.responses import JSONResponse, HTMLResponse

from app.web.htmx_templates import htmx_fragment, htmx_error
from app.core.chat_core import ChatCore

router = APIRouter()
chat_core = ChatCore()


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
    return htmx_fragment("Usuario", message, "Asistente", response)


def process_message(message):
    if not message:
        raise ValueError("No se proporcionó ningún mensaje.")

    return chat_core.handle_message(message)


# --- Builders ---

def extract_message(data):
    return data.get("message")


def handle_error_response(error, is_htmx=False):
    error_msg = f"Error interno: {str(error)}"
    if is_htmx:
        return htmx_error(error_msg)
    else:
        return JSONResponse(content={"error": error_msg}, status_code=500)