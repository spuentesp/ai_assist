import json
from .adapters.deepseek_adapter import ask_deepseek
from .adapters.ollama_adapter import ask_ollama

with open("app/llm_clients/llm_config.json") as f:
    config = json.load(f)

adapter_map = {
    "ollama": ask_ollama,
    "deepseek": ask_deepseek
}

def ask_llm(prompt):
    for model_key in config["priority"]:
        model_conf = config["models"].get(model_key)
        if not model_conf or not model_conf.get("enabled"):
            continue

        try:
            model_name = model_conf["model_name"]
            return adapter_map[model_key](prompt, model_name)
        except Exception as e:
            print(f"[WARN] Fallo modelo {model_key}: {e}")
            if not config.get("fallback_enabled"):
                raise

    raise RuntimeError("No hay modelos disponibles o todos fallaron.")
