from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.chat_core import ChatCore
from app.utils.error_handler import handle_error_response

router = APIRouter()
core = ChatCore()

@router.post("/chat")
async def chat_api(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        response = core.handle_message(message)
        return JSONResponse({"response": response})
    except Exception as e:
        return handle_error_response(e)
