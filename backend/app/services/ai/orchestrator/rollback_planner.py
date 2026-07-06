from typing import List
from app.services.ai.orchestrator.orchestration_models import RollbackPlan, ExecutionStep

class RollbackPlanner:
    def generate_rollback(self, steps: List[ExecutionStep]) -> RollbackPlan:
        # Reversing the execution steps for rollback
        commands = []
        for step in reversed(steps):
            if step.rollback and step.rollback != "N/A":
                commands.append(step.rollback)
                
        strategy = "Execute inverse AWS CLI commands in reverse order."
        if not commands:
            strategy = "Manual intervention required. Restore from latest backup or state file."
            commands = ["Manual Restore"]
            
        return RollbackPlan(
            strategy=strategy,
            commands=commands
        )
