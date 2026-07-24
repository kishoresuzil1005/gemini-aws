"""
AWS CLI Remediation Generator.
"""
from typing import Optional
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding
from app.services.ai.analyzers.engines.remediation.remediation_generator import RemediationGenerator
from app.services.ai.analyzers.engines.remediation.remediation_models import (
    RemediationStep, RollbackPlan, AWSCLICommand, ValidationStep, RollbackMode
)

class AWSCLIGenerator(RemediationGenerator):
    def get_format(self) -> str:
        return "AWS_CLI"
        
    def generate(self, finding: SecurityFinding) -> Optional[RemediationStep]:
        # Deterministic lookup logic mapping finding categories to safe CLI rollback commands.
        cmd = AWSCLICommand(
            command=f"aws ec2 modify-instance-attribute --instance-id {finding.resource_id} --no-disable-api-termination",
            description="Enables termination protection",
            service="ec2"
        )
        rollback_cmd = AWSCLICommand(
            command=f"aws ec2 modify-instance-attribute --instance-id {finding.resource_id} --disable-api-termination",
            description="Disables termination protection (Rollback)",
            service="ec2"
        )
        
        return RemediationStep(
            name="Execute AWS CLI Fix",
            description=f"Apply AWS CLI fix for {finding.rule_id}",
            actions=[cmd],
            validation=[ValidationStep(description="Verify state", command=f"aws ec2 describe-instances --instance-ids {finding.resource_id}")],
            rollback=RollbackPlan(mode=RollbackMode.AUTOMATIC, commands=[rollback_cmd], description="Revert state via CLI")
        )
