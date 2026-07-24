"""
Identity Center Security Rules.
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

class IdentityCenterBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool:
        return True

class IdentityCenterMFADisabledRule(IdentityCenterBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-SSO-001", version="1.0.0", name="Identity Center MFA Disabled", description="MFA is not enforced in AWS Identity Center.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY,
            capability=RuleCapability.DETECTIVE, severity=Severity.CRITICAL, resource_types=["IdentityCenter"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "IdentityCenter"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("mfa_enforced", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="IdentityCenter", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="MFA not enforced.", technical_impact="Federated users can login without MFA.", business_impact="Complete breach risk.",
                recommendation="Enforce MFA in Identity Center.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="IdentityCenter", expected=True, actual=False, reason="mfa_enforced is False", property="mfa_enforced", raw_data=config)
            )
        return None

class IdentityCenterRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            IdentityCenterMFADisabledRule()
        ]
