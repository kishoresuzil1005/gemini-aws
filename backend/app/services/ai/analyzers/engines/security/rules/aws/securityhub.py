"""
SecurityHub Security Rules.
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

class SecurityHubBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool:
        return True

class SecurityHubGuardDutyDisabledRule(SecurityHubBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-SH-001", version="1.0.0", name="GuardDuty Disabled", description="Amazon GuardDuty is disabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.MONITORING,
            capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["AWSAccount"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "AWSAccount"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("guardduty_enabled", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="AWSAccount", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Service not enabled.", technical_impact="Missing threat detection.", business_impact="Blind to malicious activity.",
                recommendation="Enable GuardDuty in all regions.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="AWSAccount", expected=True, actual=False, reason="guardduty_enabled is False", property="guardduty_enabled", raw_data=config)
            )
        return None

class SecurityHubInspectorDisabledRule(SecurityHubBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-SH-002", version="1.0.0", name="Inspector Disabled", description="Amazon Inspector is disabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.MONITORING,
            capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["AWSAccount"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED]
        )
    def supports(self, node_type: str) -> bool: return node_type == "AWSAccount"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("inspector_enabled", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="AWSAccount", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Service not enabled.", technical_impact="Vulnerabilities unmanaged.", business_impact="Unpatched systems risk.",
                recommendation="Enable Amazon Inspector.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="AWSAccount", expected=True, actual=False, reason="inspector_enabled is False", property="inspector_enabled", raw_data=config)
            )
        return None

class SecurityHubConfigDisabledRule(SecurityHubBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-SH-003", version="1.0.0", name="AWS Config Disabled", description="AWS Config is disabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.GOVERNANCE,
            capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["AWSAccount"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "AWSAccount"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("config_enabled", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="AWSAccount", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Service not enabled.", technical_impact="No configuration history.", business_impact="Compliance gaps.",
                recommendation="Enable AWS Config globally.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="AWSAccount", expected=True, actual=False, reason="config_enabled is False", property="config_enabled", raw_data=config)
            )
        return None

class SecurityHubMacieDisabledRule(SecurityHubBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-SH-004", version="1.0.0", name="Macie Disabled", description="Amazon Macie is disabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.MONITORING,
            capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["AWSAccount"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED]
        )
    def supports(self, node_type: str) -> bool: return node_type == "AWSAccount"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("macie_enabled", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="AWSAccount", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Service not enabled.", technical_impact="S3 PII not scanned.", business_impact="Data leakage risk.",
                recommendation="Enable Amazon Macie.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="AWSAccount", expected=True, actual=False, reason="macie_enabled is False", property="macie_enabled", raw_data=config)
            )
        return None

class SecurityHubWAFMissingRule(SecurityHubBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-SH-005", version="1.0.0", name="WAF Missing", description="AWS WAF is not associated with web resources.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK,
            capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["ALB", "CloudFront", "APIGateway"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.PCI_DSS]
        )
    def supports(self, node_type: str) -> bool: return node_type in ["ALB", "CloudFront", "APIGateway"]
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("web_acl_id"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type=graph.get_node(node_id).get("type", "WebResource"), category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="No WAF ACL attached.", technical_impact="Vulnerable to layer 7 attacks.", business_impact="Potential exploitation.",
                recommendation="Attach AWS WAF WebACL.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type=graph.get_node(node_id).get("type", "WebResource"), expected="WAF ARN", actual=None, reason="web_acl_id is missing", property="web_acl_id", raw_data=config)
            )
        return None


class SecurityHubRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            SecurityHubGuardDutyDisabledRule(),
            SecurityHubInspectorDisabledRule(),
            SecurityHubConfigDisabledRule(),
            SecurityHubMacieDisabledRule(),
            SecurityHubWAFMissingRule()
        ]
