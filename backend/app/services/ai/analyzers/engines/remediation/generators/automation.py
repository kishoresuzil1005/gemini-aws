"""
Automation Workflow Remediation Generator.
"""
from typing import Optional
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding
from app.services.ai.analyzers.engines.remediation.remediation_generator import RemediationGenerator
from app.services.ai.analyzers.engines.remediation.remediation_models import (
    RemediationStep, RollbackPlan, ShellCommand, ValidationStep, RollbackMode
)

class AutomationGenerator(RemediationGenerator):
    def get_format(self) -> str:
        return "AUTOMATION"
        
    def generate(self, finding: SecurityFinding) -> Optional[RemediationStep]:
        # Represents an orchestration wrapper (e.g., Jenkins pipeline script, GitHub Actions YAML)
        cmd = ShellCommand(
            command=f"trigger_workflow.sh --finding {finding.rule_id} --resource {finding.resource_id} --action remediate",
            description="Triggers the central automation platform",
            is_sudo_required=False
        )
        rollback_cmd = ShellCommand(
            command=f"trigger_workflow.sh --finding {finding.rule_id} --resource {finding.resource_id} --action rollback",
            description="Triggers rollback on central automation platform",
            is_sudo_required=False
        )
        
        return RemediationStep(
            name="Trigger Automation Workflow",
            description=f"Orchestration pipeline hook for {finding.rule_id}",
            actions=[cmd],
            validation=[ValidationStep(description="Wait for pipeline success")],
            rollback=RollbackPlan(mode=RollbackMode.AUTOMATIC, commands=[rollback_cmd], description="Trigger rollback workflow")
        )
