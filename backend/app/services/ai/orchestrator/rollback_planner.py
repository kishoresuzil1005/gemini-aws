from typing import List
from app.services.ai.orchestrator.orchestration_models import RollbackPlan, ExecutionStep

class RollbackPlanner:
    def generate_rollback(self, steps: List[ExecutionStep]) -> RollbackPlan:
        # Reversing the execution steps for rollback
        commands = []
        step_index = 1
        for step in reversed(steps):
            if step.rollback and step.rollback != "N/A":
                commands.append(ExecutionStep(
                    id=f"rollback-{step_index}",
                    title=f"Revert: {step.title}",
                    action="Rollback",
                    command=step.rollback,
                    estimated_time="1m",
                    rollback="N/A"
                ))
                step_index += 1
                
        strategy = "Execute inverse AWS CLI commands in reverse order."
        if not commands:
            strategy = "Manual intervention required. Restore from latest backup or state file."
            commands = [ExecutionStep(
                id="rollback-1",
                title="Manual Restore",
                action="Rollback",
                command="Manual Intervention",
                estimated_time="15m",
                rollback="N/A"
            )]
            
        return RollbackPlan(
            strategy=strategy,
            commands=commands
        )