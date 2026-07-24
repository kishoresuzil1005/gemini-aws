"""
CloudTrail Security Rules.
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

class CloudTrailBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool:
        return True

class CloudTrailDisabledRule(CloudTrailBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-CT-001", version="1.0.0", name="CloudTrail Disabled", description="CloudTrail is not enabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.LOGGING,
            capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["CloudTrail"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "CloudTrail"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("is_logging", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="CloudTrail", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Trail logging is turned off.", technical_impact="No API auditing.", business_impact="Compliance failure.",
                recommendation="Enable CloudTrail logging.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="CloudTrail", expected=True, actual=False, reason="is_logging is False", property="is_logging", raw_data=config)
            )
        return None

class CloudTrailEncryptionRule(CloudTrailBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-CT-002", version="1.0.0", name="CloudTrail Encryption Disabled", description="CloudTrail does not use KMS encryption.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.ENCRYPTION,
            capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["CloudTrail"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "CloudTrail"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("kms_key_id"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="CloudTrail", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="KMS key not configured.", technical_impact="Logs stored without KMS encryption.", business_impact="Security standard violation.",
                recommendation="Configure KMS Key for Trail.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="CloudTrail", expected="KMS Key ARN", actual=None, reason="kms_key_id is empty", property="kms_key_id", raw_data=config)
            )
        return None

class CloudTrailMultiRegionRule(CloudTrailBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-CT-003", version="1.0.0", name="CloudTrail Multi-Region Disabled", description="CloudTrail is not multi-region.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.LOGGING,
            capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["CloudTrail"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "CloudTrail"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("is_multi_region_trail", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="CloudTrail", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Trail is single region.", technical_impact="Will not log global/other region events.", business_impact="Visibility gaps.",
                recommendation="Enable multi-region trail.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="CloudTrail", expected=True, actual=False, reason="is_multi_region_trail is False", property="is_multi_region_trail", raw_data=config)
            )
        return None

class CloudTrailRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            CloudTrailDisabledRule(),
            CloudTrailEncryptionRule(),
            CloudTrailMultiRegionRule()
        ]
