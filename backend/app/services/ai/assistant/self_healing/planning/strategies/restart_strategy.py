from typing import Dict, Any
from ...models.healing_models import RepairPlan

class RestartStrategy:
    """
    Defines the specific steps required to safely restart a service.
    """
    def build_plan(self, incident_id: str, target: str) -> RepairPlan:
        print(f"[RestartStrategy] Formulating restart steps for {target}...")
        return RepairPlan(
            plan_id=f"rp-restart-{target}",
            incident_id=incident_id,
            objectives=[
                {"action": "drain_traffic", "target": target},
                {"action": "reboot_instance", "target": target},
                {"action": "health_check", "target": target},
                {"action": "restore_traffic", "target": target}
            ],
            requires_approval=False,
            confidence=95.0
        