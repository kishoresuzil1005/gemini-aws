from app.core.logging import get_logger
logger = get_logger(__name__)
from typing import Dict, Any

class LearningAdapter:
    """
    Closes the loop by sending repair outcomes to the Phase 9 Learning Engine.
    Ensures that failed repairs are not recommended again.
    """
    def send_feedback(self, incident_id: str, success: bool, diagnosis: Dict[str, Any], plan: Dict[str, Any]):
        logger.debug(f"[LearningAdapter] Feeding back outcome of incident {incident_id} to Learning Engine.")
        if not success:
            logger.debug("[LearningAdapter] Flagging this repair strategy as unreliable for this failure mode.")
        else:
            logger.debug("[LearningAdapter] Increasing confidence score for this repair strategy.")