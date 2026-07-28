from app.core.logging import get_logger
logger = get_logger(__name__)
from typing import Dict, Any
from ..models.healing_models import RepairPlan

class SafetyEngine:
    """
    Enforces organizational policies (e.g. 'Never delete production DB automatically').
    """
    def validate_plan_safety(self, plan: RepairPlan, context: Dict[str, Any]) -> bool:
        logger.debug("[SafetyEngine] Evaluating repair plan against safety policies...")
        if context.get("environment") == "production" and "delete" in str(plan.objectives).lower():
            logger.debug("[SafetyEngine] BLOCKED: Destructive action in production requires manual approval.")
            return False
        return True