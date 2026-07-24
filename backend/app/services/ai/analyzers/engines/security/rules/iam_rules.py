"""
IAM Security Rules.
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

class IAMWildcardPolicyRule(SecurityRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-IAM-001",
            version="1.0.0",
            name="IAM Policy allows Wildcard Actions",
            description="IAM Policy grants '*' permissions.",
            provider=CloudProvider.AWS,
            domain=SecurityDomain.AWS,
            category=SecurityCategory.IDENTITY,
            capability=RuleCapability.DETECTIVE,
            severity=Severity.HIGH,
            status=RuleStatus.ENABLED,
            created_version="1.0.0",
            tags=["iam", "privilege-escalation"]
        )
        
    def supports(self, node_type: str) -> bool:
        return node_type in ["IAMPolicy", "IAMRole"]
        
    def compliance(self) -> List[ComplianceFramework]: 
        return [ComplianceFramework.CIS, ComplianceFramework.SOC2]
        
    def validate(self) -> bool: return True
    
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        node = graph.get_node(node_id)
        policy_document = node.get("configuration", {}).get("policy_document", {})
        statements = policy_document.get("Statement", [])
        if isinstance(statements, dict):
            statements = [statements]
            
        for statement in statements:
            if statement.get("Effect") == "Allow":
                actions = statement.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                
                if "*" in actions:
                    evidence = Evidence(
                        resource_id=node_id,
                        resource_type=node.get("type", "IAMPolicy"),
                        expected="Explicit scoped actions",
                        actual="Wildcard '*'",
                        reason="Action is set to '*' in an Allow statement.",
                        property="policy_document.Statement.Action",
                        raw_data=statement
                    )
                    return SecurityFinding(
                        rule_id=self.metadata().id,
                        rule_name=self.metadata().name,
                        resource_id=node_id,
                        resource_type=node.get("type", "IAMPolicy"),
                        category=self.metadata().category,
                        base_severity=self.metadata().severity,
                        description=self.metadata().description,
                        root_cause="Policy uses wildcard permissions instead of least privilege.",
                        technical_impact="Compromise of this principal grants complete control over the AWS account.",
                        business_impact="Total account takeover leading to massive financial and data loss.",
                        recommendation="Restrict permissions to least privilege by explicitly naming required actions.",
                        compliance_mapping=self.compliance(),
                        evidence=evidence,
                        automation_possible=False
                    )
        return None
