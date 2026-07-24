"""
Organizations Security Rules.
"""
from typing import List, Optional, Any, Dict
from app.services.ai.analyzers.base.analyzer_models import CloudProvider, Severity
from app.services.ai.analyzers.engines.security.security_rule import SecurityRule
from app.services.ai.analyzers.engines.security.security_rule_group import SecurityRuleGroup
from app.services.ai.analyzers.engines.security.security_models import (
    SecurityFinding, ComplianceFramework, SecurityCategory, SecurityDomain, 
    RuleMetadata, RuleCapability, RuleStatus, Evidence
)
from app.services.ai.analyzers.engines.graph.infrastructure_graph import InfrastructureGraph
from app.services.ai.analyzers.engines.context.engine_context import EngineContext

class OrganizationsBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool:
        return True

class OrganizationsMissingSCPRule(OrganizationsBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-ORG-001", version="1.0.0", name="Missing SCP", description="No Service Control Policies attached to account or OU.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.GOVERNANCE,
            capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["AWSAccount", "OrganizationalUnit"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED]
        )
    def supports(self, node_type: str) -> bool: return node_type in ["AWSAccount", "OrganizationalUnit"]
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        # Verify if it has SCPs other than the default FullAWSAccess
        scps = config.get("attached_scps", [])
        has_custom_scp = any("FullAWSAccess" not in scp.get("name", "") for scp in scps)
        
        if not has_custom_scp:
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type=graph.get_node(node_id).get("type", "AWSAccount"), category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="No custom SCPs attached.", technical_impact="No central guardrails.", business_impact="Governance violation.",
                recommendation="Attach custom Service Control Policies to enforce guardrails.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type=graph.get_node(node_id).get("type", "AWSAccount"), expected="Custom SCP", actual="FullAWSAccess or None", reason="No custom SCPs found.", property="attached_scps", raw_data=config)
            )
        return None

class OrganizationsRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            OrganizationsMissingSCPRule()
        ]
