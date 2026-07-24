"""
AWS Backup Security Rules.
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

class BackupBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool:
        return True

class BackupMissingPlanRule(BackupBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-BACKUP-001", version="1.0.0", name="Missing Backup Plan", description="Critical resource is not covered by AWS Backup.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.RESILIENCE,
            capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["RDS", "DynamoDB", "EFS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.SOC2]
        )
    def supports(self, node_type: str) -> bool: return node_type in ["RDS", "DynamoDB", "EFS"]
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("aws_backup_enabled", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type=graph.get_node(node_id).get("type", "Resource"), category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Resource lacks AWS Backup plan.", technical_impact="Cannot recover from data loss centrally.", business_impact="Data loss risk.",
                recommendation="Assign resource to an AWS Backup Plan.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type=graph.get_node(node_id).get("type", "Resource"), expected=True, actual=False, reason="aws_backup_enabled is False", property="aws_backup_enabled", raw_data=config)
            )
        return None

class BackupRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            BackupMissingPlanRule()
        ]
