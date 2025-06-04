from fastapi.responses import JSONResponse, HTMLResponse
from fastapi import HTTPException
from app.builders import htmx_builder

def handle_error_response(error: Exception, is_htmx: bool = False):
    # Valores por defecto
    status_code = 500
    message = "Error interno"

    # Si es una HTTPException, usar su status y detalle
    if isinstance(error, HTTPException):
        status_code = error.status_code
        message = error.detail
    else:
        message = str(error)

    # HTMX (HTML)
    if is_htmx:
        html = htmx_builder.build_error_response(message)
        return HTMLResponse(content=html, status_code=status_code)

    # JSON API
    return JSONResponse(content={"error": message}, status_code=status_code)
