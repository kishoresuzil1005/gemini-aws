from typing import Dict, Any
from ..models.mission_models import MissionResult

class LearningEngine:
    """
    Updated LearningEngine that consumes MissionResult instead of only WorkflowResult.
    """
    def process_mission_result(self, result: MissionResult):
        print(f"[LearningEngine] Learning from completed mission: {result.mission_id}")
        if result.status == "COMPLETED":
            print("[LearningEngine] Storing successful strategies for future missions.")
        else:
            print("[LearningEngine] Analyzing failure points in mission.")
