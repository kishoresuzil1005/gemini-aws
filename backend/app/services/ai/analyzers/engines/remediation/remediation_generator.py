"""
Abstract Interfaces for Remediation Generators.
"""
from abc import ABC, abstractmethod
from typing import Optional
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding
from app.services.ai.analyzers.engines.remediation.remediation_models import RemediationStep

class RemediationGenerator(ABC):
    """
    Abstract interface for all output format generators (e.g., AWS CLI, Terraform).
    """
    
    @abstractmethod
    def get_format(self) -> str:
        """Returns the format this generator produces (e.g., 'AWS_CLI', 'TERRAFORM')."""
        pass
        
    @abstractmethod
    def generate(self, finding: SecurityFinding) -> Optional[RemediationStep]:
        """
        Consumes a generic finding and returns a typed RemediationStep containing
        actions (commands/HCL/YAML), validation steps, and rollback plans.
        Returns None if this generator cannot handle the finding.
        """
        pass
