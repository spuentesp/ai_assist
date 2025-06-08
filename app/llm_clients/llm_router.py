import json
import app.llm_clients.adapters.deepseek_adapter
import app.llm_clients.adapters.ollama_adapter
import app.llm_clients.adapters.mistral_adapter
from .adapters.adapter_registry import adapter_map

# Carga la configuración de prioridad y modelos habilitados
with open("app/llm_clients/llm_config.json") as f:
    config = json.load(f)


def ask_llm(prompt):
    for model_key in config["priority"]:
        model_conf = config["models"].get(model_key)
        if not model_conf or not model_conf.get("enabled"):
            continue

        try:
            model_name = model_conf["model_name"]
            return adapter_map[model_key]["ask"](prompt, model_name)
        except Exception as e:
            print(f"[WARN] Falló el modelo {model_key}: {e}")
            if not config.get("fallback_enabled"):
                raise

    raise RuntimeError("No hay modelos disponibles o todos fallaron.")


def get_embedding_function():
    for model_key in config["priority"]:
        model_conf = config["models"].get(model_key)
        if not model_conf or not model_conf.get("enabled"):
            continue

        try:
            model_name = model_conf["model_name"]
            return adapter_map[model_key]["get_embedding_function"](
                model=model_name
            )
        except Exception as e:
            print(f"[WARN] Falló función de embedding para {model_key}: {e}")
            if not config.get("fallback_enabled"):
                raise

    raise RuntimeError("No hay funciones de embedding disponibles.")


def get_embedding_model_and_config():
    for model_key in config["priority"]:
        model_conf = config["models"].get(model_key)
        if not model_conf or not model_conf.get("enabled"):
            continue

        try:
            model_name = model_conf["model_name"]
            return model_key, {"model": model_name}
        except Exception as e:
            print(
                f"[WARN] Falló función de configuración para {model_key}: {e}")
            if not config.get("fallback_enabled"):
                raise

    raise RuntimeError("No hay funciones de embedding disponibles.")
