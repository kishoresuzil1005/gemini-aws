from typing import Dict, Any

class ModelRegistry:
    """Manages progression of models: Rule-Based -> Statistical -> ML -> LLM."""
    
    def __init__(self):
        self._models = {}
        
    def register_model(self, name: str, model_instance: Any, version: str = "v1"):
        self._models[f"{name}_{version}"] = model_instance
        
    def get_model(self, name: str, version: str = "v1"):
        return self._models.get(f"{name}_{version}")
