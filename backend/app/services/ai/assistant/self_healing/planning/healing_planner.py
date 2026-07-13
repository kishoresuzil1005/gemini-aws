from typing import Dict, Any
from ..models.healing_models import Incident, RepairPlan

class HealingPlanner:
    """
    Transforms a diagnosis into a step-by-step repair strategy (Workflow/Mission objectives).
    """
    def create_repair_plan(self, incident: Incident, diagnosis: Dict[str, Any]) -> RepairPlan:
        print("[HealingPlanner] Formulating safe remediation plan...")
        return RepairPlan(
            plan_id="rp-001",
            incident_id=incident.incident_id,
            objectives=[{"action": "restart_service", "target": diagnosis["root_cause_node"]}],
            requires_approval=False,
            confidence=94.5
        