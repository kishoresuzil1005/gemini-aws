"""
Shell Script Remediation Generator.
"""
from typing import Optional
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding
from app.services.ai.analyzers.engines.remediation.remediation_generator import RemediationGenerator
from app.services.ai.analyzers.engines.remediation.remediation_models import (
    RemediationStep, RollbackPlan, ShellCommand, ValidationStep, RollbackMode
)

class ShellGenerator(RemediationGenerator):
    def get_format(self) -> str:
        return "SHELL"
        
    def generate(self, finding: SecurityFinding) -> Optional[RemediationStep]:
        cmd = ShellCommand(
            command=f"#!/bin/bash\necho 'Fixing {finding.resource_id}...'\n# Add fix logic here",
            description="Bash script to apply fix",
            is_sudo_required=False
        )
        rollback_cmd = ShellCommand(
            command=f"#!/bin/bash\necho 'Reverting {finding.resource_id}...'\n# Add revert logic here",
            description="Bash script to rollback fix",
            is_sudo_required=False
        )
        
        return RemediationStep(
            name="Execute Bash Script",
            description=f"Bash script for {finding.rule_id}",
            actions=[cmd],
            validation=[ValidationStep(description="Check exit code", command="echo $?")],
            rollback=RollbackPlan(mode=RollbackMode.AUTOMATIC, commands=[rollback_cmd], description="Revert via script")
        )
