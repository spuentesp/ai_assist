def build_enriched_prompt(message: str, short_context_str: str, long_context_str: str) -> str:
    return f"""Contexto corto plazo:
{short_context_str}

Contexto largo plazo:
{long_context_str}

Pregunta:
{message}
"""
