"""
Security Rule Interface.
Every rule must implement this strict deterministic contract.
Rules are immutable. Only findings are mutable.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.services.ai.analyzers.base.analyzer_models import SupportedResource
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph
from app.services.ai.analyzers.engines.context.engine_context import EngineContext
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding, ComplianceFramework, RuleMetadata

class SecurityRule(ABC):
    
    @abstractmethod
    def metadata(self) -> RuleMetadata:
        """Exposes the immutable RuleMetadata (version, capability, domain, etc.)"""
        pass
        
    def version(self) -> str:
        """Convenience accessor for semantic version."""
        return self.metadata().version
        
    @abstractmethod
    def supports(self, node_type: str) -> bool:
        """Quick check if this rule supports the given node type (e.g., 'S3Bucket')."""
        pass
        
    @abstractmethod
    def compliance(self) -> List[ComplianceFramework]:
        pass
        
    @abstractmethod
    def validate(self) -> bool:
        """Self-check capability to ensure the rule is configured correctly."""
        pass
        
    @abstractmethod
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        """
        Deterministically evaluates a single node.
        Returns a SecurityFinding containing strict Evidence if a violation exists, else None.
        Must NOT call AWS, LLM, or mutate the graph.
        """
        pass
