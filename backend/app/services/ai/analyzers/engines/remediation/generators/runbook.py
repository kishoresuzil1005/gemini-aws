"""
Runbook Remediation Generator.
"""
from typing import Optional
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding
from app.services.ai.analyzers.engines.remediation.remediation_generator import RemediationGenerator
from app.services.ai.analyzers.engines.remediation.remediation_models import (
    RemediationStep, RollbackPlan, Runbook, ValidationStep, RollbackMode
)

class RunbookGenerator(RemediationGenerator):
    def get_format(self) -> str:
        return "RUNBOOK"
        
    def generate(self, finding: SecurityFinding) -> Optional[RemediationStep]:
        cmd = Runbook(
            title=f"Manual Runbook for {finding.rule_id}",
            steps=[
                f"1. Login to AWS Console for account containing {finding.resource_id}.",
                "2. Navigate to the specific service dashboard.",
                "3. Locate the resource and click Edit.",
                f"4. Apply the recommended change: {finding.recommendation}",
                "5. Save changes."
            ]
        )
        rollback_cmd = Runbook(
            title=f"Rollback Runbook for {finding.rule_id}",
            steps=[
                f"1. Locate resource {finding.resource_id} in AWS Console.",
                "2. Revert the applied change back to previous state.",
                "3. Save changes."
            ]
        )
        
        return RemediationStep(
            name="Follow Runbook",
            description=f"Step-by-step instructions for {finding.rule_id}",
            actions=[cmd],
            validation=[ValidationStep(description="Verify visually in console")],
            rollback=RollbackPlan(mode=RollbackMode.MANUAL, commands=[rollback_cmd], description="Manual revert steps")
        )
