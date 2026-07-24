"""
RDS Security Rules.
"""
from typing import List, Optional
from app.services.ai.analyzers.base.analyzer_models import CloudProvider, Severity
from app.services.ai.analyzers.engines.security.security_rule import SecurityRule
from app.services.ai.analyzers.engines.security.security_models import (
    SecurityFinding, ComplianceFramework, SecurityCategory, SecurityDomain, 
    RuleMetadata, RuleCapability, RuleStatus, Evidence
)
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph
from app.services.ai.analyzers.engines.context.engine_context import EngineContext

class RDSPublicAccessRule(SecurityRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-RDS-001",
            version="1.0.0",
            name="RDS Instance Publicly Accessible",
            description="RDS instance is marked as Publicly Accessible.",
            provider=CloudProvider.AWS,
            domain=SecurityDomain.AWS,
            category=SecurityCategory.DATABASE,
            capability=RuleCapability.DETECTIVE,
            severity=Severity.CRITICAL,
            status=RuleStatus.ENABLED,
            created_version="1.0.0",
            tags=["rds", "database", "exposure"]
        )
        
    def supports(self, node_type: str) -> bool:
        return node_type == "RDS"
        
    def compliance(self) -> List[ComplianceFramework]: 
        return [ComplianceFramework.CIS, ComplianceFramework.PCI_DSS]
        
    def validate(self) -> bool: return True
    
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        node = graph.get_node(node_id)
        config = node.get("configuration", {})
        
        is_public = config.get("publicly_accessible")
        if is_public is True:
            evidence = Evidence(
                resource_id=node_id,
                resource_type="RDS",
                expected={"publicly_accessible": False},
                actual={"publicly_accessible": True},
                reason="PubliclyAccessible flag is set to True.",
                property="publicly_accessible",
                raw_data={"publicly_accessible": True}
            )
            return SecurityFinding(
                rule_id=self.metadata().id,
                rule_name=self.metadata().name,
                resource_id=node_id,
                resource_type="RDS",
                category=self.metadata().category,
                base_severity=self.metadata().severity,
                description=self.metadata().description,
                root_cause="Instance configured with public routing.",
                technical_impact="Database ports are exposed to global port scans and brute force attacks.",
                business_impact="Critical risk of primary database compromise and massive data loss.",
                recommendation="Set PubliclyAccessible to False and move instance to a private subnet.",
                compliance_mapping=self.compliance(),
                evidence=evidence,
                automation_possible=True
            )
        return None
