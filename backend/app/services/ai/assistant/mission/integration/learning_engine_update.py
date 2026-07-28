from app.core.logging import get_logger
logger = get_logger(__name__)
from typing import Dict, Any
from ..models.mission_models import MissionResult

class LearningEngine:
    """
    Updated LearningEngine that consumes MissionResult instead of only WorkflowResult.
    """
    def process_mission_result(self, result: MissionResult):
        logger.debug(f"[LearningEngine] Learning from completed mission: {result.mission_id}")
        if result.status == "COMPLETED":
            logger.debug("[LearningEngine] Storing successful strategies for future missions.")
        else:
            logger.debug("[LearningEngine] Analyzing failure points in mission.")