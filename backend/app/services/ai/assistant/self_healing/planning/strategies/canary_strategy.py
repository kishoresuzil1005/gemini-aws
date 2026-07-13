from typing import Dict, Any
from ...models.healing_models import RepairPlan

class CanaryStrategy:
    """
    Safely rolls out repairs (like pod restarts) in increments (1, 5, 100) 
    verifying health at each stage before proceeding.
    """
    def build_canary_plan(self, incident_id: str, target_deployment: str) -> RepairPlan:
        print(f"[CanaryStrategy] Formulating progressive canary repair for {target_deployment}...")
        return RepairPlan(
            plan_id=f"rp-canary-{target_deployment}",
            incident_id=incident_id,
            objectives=[
                {"action": "restart_nodes", "target": target_deployment, "batch_size": 1},
                {"action": "health_check", "target": target_deployment},
                {"action": "restart_nodes", "target": target_deployment, "batch_size": 5},
                {"action": "health_check", "target": target_deployment},
                {"action": "restart_nodes", "target": target_deployment, "batch_size": "ALL"},
                {"action": "health_check", "target": target_deployment}
            ],
            requires_approval=True,
            confidence=92.5
        )