"""
Abstract Base Class for Compliance Framework Plugins.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.services.ai.analyzers.engines.compliance.compliance_models import (
    ComplianceFramework, FrameworkVersion, ComplianceRequirement
)
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding

class ComplianceFrameworkDefinition(ABC):
    """
    Interface for mapping raw SecurityFindings to structured Compliance Requirements/Controls.
    """
    
    @abstractmethod
    def get_framework_type(self) -> ComplianceFramework:
        """Return the framework enum this definition represents."""
        pass
        
    @abstractmethod
    def get_version(self) -> FrameworkVersion:
        """Return the version information of this framework."""
        pass
        
    @abstractmethod
    def map_findings(self, findings: List[SecurityFinding]) -> List[ComplianceRequirement]:
        """
        Consumes SecurityFindings that matched this framework in their RuleMetadata,
        and aggregates them into the framework's official Requirement/Control structure.
        """
        pass
