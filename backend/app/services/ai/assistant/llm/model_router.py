from typing import Dict, Any

class ModelRouter:
    """
    Routes inference requests to the optimal Ollama model based on task type.
    """
    def __init__(self):
        self.model_map = {
            "architecture": "llama3",
            "security": "llama3",
            "terraform": "deepseek-coder",
            "kubernetes": "llama3",
            "finops": "qwen2",
            "sre": "llama3",
            "mission": "llama3",
            "code": "deepseek-coder",
            "default": "llama3"
        }

    def select_model(self, intent: str) -> str:
        selected = self.model_map.get(intent, self.model_map["default"])
        print(f"[ModelRouter] Intent='{intent}' -> Model='{selected}'")
        return selected