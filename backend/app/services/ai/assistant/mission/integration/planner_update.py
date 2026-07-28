from app.core.logging import get_logger
logger = get_logger(__name__)
from typing import Dict, Any
from ..models.mission_models import MissionGoal

class MissionPlanner:
    """
    Updated Planner that now returns MissionPlans (or MissionGoals) for long-running goals
    instead of just ExecutionPlans.
    """
    def generate_mission_plan(self, intent: str) -> MissionGoal:
        logger.debug("[Planner] Generating MissionPlan instead of a single ExecutionPlan.")
        # Integrate with GoalEngine underneath
        return MissionGoal(
            description=intent,
            metrics={},
            objectives=[]
        )