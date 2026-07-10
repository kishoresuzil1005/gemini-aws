from typing import Dict, Any, List
from ..models.mission_models import Mission

class MissionPolicy:
    """
    Evaluates organizational rules and boundaries for missions before validation.
    Separates business/security policy from technical validation.
    """
    def __init__(self):
        self.blocked_actions = ["Delete Production Database", "Disable Global MFA"]

    def evaluate(self, mission: Mission) -> Dict[str, Any]:
        """
        Checks if the mission intent or goal violates any core organizational policies.
        """
        intent = mission.intent.lower()
        for blocked in self.blocked_actions:
            if blocked.lower() in intent:
                print(f"[MissionPolicy] REJECTED: Mission intent violates policy '{blocked}'")
                return {"allowed": False, "reason": f"Violates policy: {blocked}"}
                
        for obj in mission.goal.objectives:
            if "delete" in obj.description.lower() and "production" in str(mission.context).lower():
                print(f"[MissionPolicy] REJECTED: Deletion in production environment is blocked by policy.")
                return {"allowed": False, "reason": "Production deletion blocked."}
                
        return {"allowed": True, "reason": "Compliant"}
