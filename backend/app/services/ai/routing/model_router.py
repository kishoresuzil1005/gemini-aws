from typing import Dict, Any
from app.services.ai.routing.model_profiles import MODEL_PROFILES
from app.services.ai.routing.task_planner import TaskType

class ModelRouter:
    @staticmethod
    def select_profile(task_type: TaskType, complexity: int, resource_count: int) -> Dict[str, Any]:
        if task_type == TaskType.SECURITY:
            return MODEL_PROFILES["REASONING"]
        
        if complexity >= 7:
            return MODEL_PROFILES["PLANNING"]
        elif complexity >= 4:
            return MODEL_PROFILES["REASONING"]
        else:
            return MODEL_PROFILES["FAST"]
