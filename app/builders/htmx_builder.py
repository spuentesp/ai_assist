def build_chat_response(message: str, response: str) -> str:
    return f"""
    <hr>
    <div class='message user'><strong>Usuario:</strong> {message}</div>
    <div class='message bot'><strong>Asistente:</strong> {response}</div>
    """

def build_error_response(error_msg: str) -> str:
    return f"<div class='message error'><strong>Error:</strong> {error_msg}</div>"

def build_system_message(message: str) -> str:
    return f"<div class='message system'><em>{message}</em></div>"