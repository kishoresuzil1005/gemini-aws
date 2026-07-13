from app.services.ai.assistant.actions.action_models import ActionPlan, RollbackPlan
from app.services.ai.assistant.actions.action_rules import ACTION_POLICIES

class RollbackManager:
    def prepare_rollback(self, plan: ActionPlan) -> RollbackPlan:
        """
        Calculates and stores rollback state logic (e.g. Snapshot IDs).
        Does not execute rollbacks.
        """
        policy = ACTION_POLICIES.get(plan.request.action_name, {})
        is_possible = policy.get("rollback_possible", False)
        
        if not is_possible:
            return RollbackPlan(rollback_available=False)
            
        return RollbackPlan(
            rollback_available=True,
            snapshot_ids=[f"snap-{plan.request.resource_id}"],
            rollback_commands=[f"restore {plan.request.resource_id}"],
            dependencies=[]
        )