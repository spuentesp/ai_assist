from fastapi.responses import HTMLResponse


def htmx_fragment(message: str, response: str) -> HTMLResponse:
    """
    Builds an HTML fragment formatted for HTMX response.

    Args:
        message (str): User message.
        response (str): Assistant response.

    Returns:
        HTMLResponse: HTML snippet formatted for HTMX.
    """
    html = f"""
    <hr>
    <div class='message user'><strong>Usuario:</strong> {message}</div>
    <div class='message bot'><strong>Asistente:</strong> {response}</div>
    """
    return HTMLResponse(content=html)


def htmx_error(message: str) -> HTMLResponse:
    """
    Returns a formatted HTML error block.

    Args:
        message (str): Error message to display.

    Returns:
        HTMLResponse: HTML error display.
    """
    html = f"<div class='message error'><strong>Error:</strong> {message}</div>"
    return HTMLResponse(content=html, status_code=500)
