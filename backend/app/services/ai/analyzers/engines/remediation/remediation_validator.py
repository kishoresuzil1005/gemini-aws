"""
Remediation Validator to ensure safety and completeness.
"""
from typing import List
from app.services.ai.analyzers.engines.remediation.remediation_models import RemediationStep

class RemediationValidator:
    """
    Safety gate ensuring generated commands are structurally valid and contain rollbacks.
    """
    
    @staticmethod
    def validate_step(step: RemediationStep) -> bool:
        """
        Validates that a generated remediation step is safe to present.
        Rules:
        - Must have at least one action
        - Must have a rollback plan
        - Rollback plan must not be empty unless explicitly NONE mode
        """
        if not step.actions:
            return False
            
        if not step.rollback:
            return False
            
        if step.rollback.mode.value != "NONE" and not step.rollback.commands:
            return False
            
        return True
