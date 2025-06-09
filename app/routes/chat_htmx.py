from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse
from app.core.chat_core import ChatCore
from app.builders import htmx_builder
from app.utils.error_handler import handle_error_response
from app.llm_clients.llm_router import get_embedding_model_and_config

router = APIRouter()
MASTER_TOKEN = "test"

core = ChatCore()
embedding_model, model_config = get_embedding_model_and_config()


# === AUTH ===
@router.post("/auth")
async def auth(token: str = Form(...)):
    if token == MASTER_TOKEN:
        return HTMLResponse("<div id='auth-panel'></div>")
    return HTMLResponse("<div id='auth-panel'><p class='message error'>Token inválido</p></div>", status_code=401)


# === CHAT ===
@router.post("/chat-ui")
async def chat_htmx(message: str = Form(...)):
    try:
        response = core.handle_message(message)
        return HTMLResponse(htmx_builder.build_chat_response(message, response))
    except Exception as e:
        return handle_error_response(e, is_htmx=True)


# === MEMORY FAISS ===
@router.get("/memory/faiss")
async def faiss_htmx():
    try:
        faiss_store = core.memory_orchestrator.get_store("faiss")
        html = "<pre>" + "\n".join(faiss_store.get_recent()) + "</pre>"
        return HTMLResponse(html)
    except Exception as e:
        return handle_error_response(e, is_htmx=True)


# === MEMORY CHROMA ===
@router.get("/memory/chroma")
async def chroma_htmx():
    try:
        chroma_store = core.memory_orchestrator.get_store("chroma")
        stats = chroma_store.get_stats()
        html = f"<pre>Collection: {stats.get('name', 'unknown')}\nTotal: {stats.get('count', 0)}</pre>"
        return HTMLResponse(html)
    except Exception as e:
        return handle_error_response(e, is_htmx=True)


# === LOGS ===
@router.get("/logs")
async def logs_htmx():
    try:
        with open("logs/app.log", encoding="utf-8") as f:
            lines = f.readlines()[-30:]
        return HTMLResponse("<pre>" + "".join(lines) + "</pre>")
    except FileNotFoundError:
        return HTMLResponse("<pre>No hay logs disponibles.</pre>")
    except Exception as e:
        return handle_error_response(e, is_htmx=True)


# === CONFIG VIEWER ===
@router.get("/config")
async def config_htmx(config: str = "app/llm_clients/llm_config.json"):
    try:
        with open(config, encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(f"<textarea rows='20' style='width:100%'>{content}</textarea>")
    except Exception as e:
        return handle_error_response(e, is_htmx=True)
