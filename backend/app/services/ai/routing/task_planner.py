from enum import Enum

class TaskType(str, Enum):
    DEPENDENCY = "DEPENDENCY"
    SECURITY = "SECURITY"
    PERFORMANCE = "PERFORMANCE"
    COST = "COST"
    ARCHITECTURE = "ARCHITECTURE"
    PLANNING = "PLANNING"

class TaskPlanner:
    @staticmethod
    def map_intent(intent: str) -> TaskType:
        intent = intent.upper()
        mapping = {
            "DEPENDENCY": TaskType.DEPENDENCY,
            "SECURITY": TaskType.SECURITY,
            "PERFORMANCE": TaskType.PERFORMANCE,
            "COST": TaskType.COST,
            "ARCHITECTURE": TaskType.ARCHITECTURE,
            "PLANNING": TaskType.PLANNING,
            # Fallback for unrecognized intents
        }
        return mapping.get(intent, TaskType.DEPENDENCY)
