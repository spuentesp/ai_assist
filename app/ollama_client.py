import requests

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"

def ask_ollama(prompt, model="mistral"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "Sin respuesta generada.")
    except requests.exceptions.Timeout:
        return "Error: la solicitud a Ollama excedió el tiempo de espera."
    except requests.exceptions.ConnectionError:
        return "Error: no se pudo conectar a Ollama en el host configurado."
    except requests.exceptions.HTTPError as e:
        return f"Error HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"
