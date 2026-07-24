"""
Secrets Manager Security Rules.
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

class SecretsManagerBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool:
        return True

class SecretsManagerRotationDisabledRule(SecretsManagerBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-SM-001", version="1.0.0", name="Secrets Manager Rotation Disabled", description="Secret rotation is not enabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.SECRETS,
            capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["SecretsManagerSecret"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "SecretsManagerSecret"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("rotation_enabled", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="SecretsManagerSecret", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Rotation not enabled.", technical_impact="Stale secrets could be compromised.", business_impact="Credential leak risk.",
                recommendation="Enable automatic secret rotation.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="SecretsManagerSecret", expected=True, actual=False, reason="rotation_enabled is False", property="rotation_enabled", raw_data=config)
            )
        return None

class SecretsManagerRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            SecretsManagerRotationDisabledRule()
        ]
