"""
CloudWatch Security Rules.
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

class CloudWatchBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool:
        return True

class CloudWatchMissingAlarmRule(CloudWatchBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-CW-001", version="1.0.0", name="CloudWatch Missing Alarm", description="No root account usage alarm configured.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.MONITORING,
            capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["AWSAccount"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "AWSAccount"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        # Using a representative check for missing alarms
        if not config.get("has_root_account_alarm", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="AWSAccount", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Alarm missing.", technical_impact="Will not notify on root login.", business_impact="Delayed incident response.",
                recommendation="Create a CloudWatch alarm for root account usage.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="AWSAccount", expected=True, actual=False, reason="has_root_account_alarm is False", property="has_root_account_alarm", raw_data=config)
            )
        return None

class CloudWatchMissingLogGroupRule(CloudWatchBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-CW-002", version="1.0.0", name="CloudWatch Missing Log Group", description="CloudTrail is not sending logs to CloudWatch Log Group.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.LOGGING,
            capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["CloudTrail"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "CloudTrail"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("cloudwatch_logs_log_group_arn"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="CloudTrail", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="No Log Group integration.", technical_impact="Cannot create metric filters.", business_impact="Reduced alerting capability.",
                recommendation="Integrate CloudTrail with CloudWatch Logs.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="CloudTrail", expected="Log Group ARN", actual=None, reason="cloudwatch_logs_log_group_arn is missing", property="cloudwatch_logs_log_group_arn", raw_data=config)
            )
        return None

class CloudWatchMissingRetentionRule(CloudWatchBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-CW-003", version="1.0.0", name="CloudWatch Missing Retention", description="CloudWatch Log Group has no retention policy.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.LOGGING,
            capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["CloudWatchLogGroup"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "CloudWatchLogGroup"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("retention_in_days"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="CloudWatchLogGroup", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Retention not set.", technical_impact="Logs kept indefinitely, increasing cost or not complying with data lifecycle.", business_impact="Data retention compliance failure.",
                recommendation="Set a retention period for the log group.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="CloudWatchLogGroup", expected="> 0 days", actual=None, reason="retention_in_days is missing", property="retention_in_days", raw_data=config)
            )
        return None

class CloudWatchRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            CloudWatchMissingAlarmRule(),
            CloudWatchMissingLogGroupRule(),
            CloudWatchMissingRetentionRule()
        ]
