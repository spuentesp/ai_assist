import json
from typing import List, Dict, Tuple, Any
from app.llm_clients.adapters.adapter_registry import adapter_map
from app.llm_clients.llm_router import ask_llm
from app.utils.utils import load_template, render_template

TEMPLATE_PATH = "app/llm_clients/prompts/rank_candidates.j2"

class LLMOrchestrator:
    def __init__(self, config_path: str = "app/llm_clients/llm_config.json"):
        with open(config_path) as f:
            self.config = json.load(f)
        self.adapters = adapter_map

    def ask_all(self, prompt: str) -> List[Dict[str, Any]]:
        """
        Send the same prompt to all enabled models in parallel (sync for now).
        Returns list of dicts with model and response.
        """
        candidates = []
        for model_key in self.config["priority"]:
            model_conf = self.config["models"].get(model_key)
            if not model_conf or not model_conf.get("enabled"):
                continue

            model_name = model_conf["model_name"]
            try:
                response = self.adapters[model_key]["ask"](prompt, model_name)
                candidates.append({
                    "model": model_key,
                    "response": response
                })
            except Exception as e:
                print(f"[WARN] Model {model_key} failed: {e}")

        return candidates


       
    def rank_candidates(self, query: str, candidates: List[str]) -> Tuple[str, str]:
            """
            Uses the meta-LLM to select the best answer among candidates.
            Returns the selected candidate.
            """
            prompt_str = load_template(TEMPLATE_PATH)
            rendered_prompt = render_template(prompt_str, {
            "query": query,
            "candidates": candidates
            })

            best_answer = ask_llm(rendered_prompt)
            return best_answer, rendered_prompt

    def respond(self, prompt: str) -> str:
        """
        Main entrypoint. Ask all LLMs, evaluate, and return best response.
        """
        candidates = self.ask_all(prompt)
        best = self.rank_candidates(prompt, candidates)
        return best["response"]

