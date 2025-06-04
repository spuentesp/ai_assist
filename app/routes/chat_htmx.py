from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse

from app.core.chat_core import ChatCore
from app.builders import htmx_builder
from app.utils.error_handler import handle_error_response

router = APIRouter()
core = ChatCore()

@router.post("/chat-ui")
async def chat_htmx(message: str = Form(...)):
    try:
        response = core.handle_message(message)
        return HTMLResponse(htmx_builder.build_chat_response(message, response))
    except Exception as e:
        return handle_error_response(e, is_htmx=True)