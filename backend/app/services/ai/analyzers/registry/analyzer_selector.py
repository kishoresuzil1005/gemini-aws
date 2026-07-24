"""
Selector for mapping Intents to Analyzer IDs via configurable routing.
"""
from typing import List, Dict
from pydantic import BaseModel, Field
from app.services.ai.routing.task_planner import TaskType


class RoutingConfig(BaseModel):
    """
    Strongly typed routing configuration.
    Supports future hydration from YAML/JSON/DB.
    """
    intent_map: Dict[TaskType, List[str]] = Field(
        ...,
        description="Maps intent TaskType to a list of Analyzer IDs."
    )

    @classmethod
    def default(cls) -> 'RoutingConfig':
        """Provides a backward-compatible default configuration."""
        return cls(
            intent_map={
                TaskType.DEPENDENCY: ["dependency_analyzer"],
                TaskType.SECURITY: ["security_analyzer"],
                TaskType.COST: ["cost_analyzer"],
                TaskType.PERFORMANCE: ["performance_analyzer"],
                TaskType.ARCHITECTURE: ["architecture_analyzer", "security_analyzer"],
                TaskType.PLANNING: ["architecture_analyzer", "cost_analyzer", "dependency_analyzer"]
            }
        )


class AnalyzerSelector:
    """
    Selects which Analyzer IDs should run based on the user's intent.
    Uses Dependency Injection for the routing configuration.
    """

    def __init__(self, config: RoutingConfig = None):
        """
        Initializes the selector with a specific routing configuration.
        Falls back to the default config if none provided, ensuring backward compatibility.
        """
        self.config = config or RoutingConfig.default()

    def select(self, intent: TaskType) -> List[str]:
        """
        Given a TaskType intent, returns the list of appropriate Analyzer IDs.
        
        Args:
            intent (TaskType): The classified intent.
            
        Returns:
            List[str]: A list of analyzer IDs to execute.
        """
        return self.config.intent_map.get(intent, ["dependency_analyzer"])
