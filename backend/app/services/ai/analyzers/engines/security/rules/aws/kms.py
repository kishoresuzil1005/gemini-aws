"""
KMS Security Rules.
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

class KMSBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool:
        return True

class KMSRotationDisabledRule(KMSBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-KMS-001", version="1.0.0", name="KMS Rotation Disabled", description="KMS CMK rotation is not enabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.ENCRYPTION,
            capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["KMSKey"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "KMSKey"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("key_manager") == "CUSTOMER" and not config.get("rotation_enabled", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="KMSKey", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Rotation not enabled.", technical_impact="Compromised key could be used indefinitely.", business_impact="Cryptographic compliance failure.",
                recommendation="Enable automatic key rotation.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="KMSKey", expected=True, actual=False, reason="rotation_enabled is False", property="rotation_enabled", raw_data=config)
            )
        return None

class KMSRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            KMSRotationDisabledRule()
        ]
