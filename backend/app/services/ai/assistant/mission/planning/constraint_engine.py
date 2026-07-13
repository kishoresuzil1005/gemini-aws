from typing import Dict, Any, List

class ConstraintEngine:
    """
    Manages and applies boundary conditions (budget, downtime, compliance)
    that must not be violated during mission execution.
    """
    def apply_constraints(self, mission_context: Dict[str, Any]) -> List[str]:
        constraints = []
        if mission_context.get("environment") == "production":
            constraints.append("no_downtime_allowed")
            constraints.append("require_human_approval_for_deletions")
        return constraint