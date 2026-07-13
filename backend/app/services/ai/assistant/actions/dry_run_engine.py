from typing import Optional
from app.services.ai.assistant.actions.action_models import ActionPlan, DryRunResult
from app.services.ai.assistant.actions.action_rules import ACTION_POLICIES

class DryRunEngine:
    def simulate(self, plan: ActionPlan) -> DryRunResult:
        """
        Simulates the execution of the action.
        Returns expected impact, downtime, cost, etc.
        """
        policy = ACTION_POLICIES.get(plan.request.action_name, {})
        
        # Example dynamic simulation logic
        downtime = 0
        if "RESTART" in plan.request.action_name:
            downtime = 5
        elif "STOP" in plan.request.action_name:
            downtime = -1 # Indefinite
            
        return DryRunResult(
            estimated_downtime_minutes=downtime,
            estimated_cost_change=0.0,
            affected_resources=[plan.request.resource_id],
            risk_level=policy.get("risk_level", "INFO"),
            warnings=["Simulated environment impact. Ensure backups exist."] if downtime != 0 else [],
            rollback_available=policy.get("rollback_possible", False),
            summary=f"Simulated {plan.request.action_name} on {plan.request.resource_id}. Impact: {policy.get('risk_level', 'INFO')}."
        