"""
Security Group Rules.
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

class SGOpenSSHRule(SecurityRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-VPC-001",
            version="1.0.0",
            name="Security Group allows Open SSH",
            description="Security Group permits 0.0.0.0/0 on port 22.",
            provider=CloudProvider.AWS,
            domain=SecurityDomain.AWS,
            category=SecurityCategory.NETWORK,
            capability=RuleCapability.DETECTIVE,
            severity=Severity.HIGH,
            status=RuleStatus.ENABLED,
            created_version="1.0.0",
            tags=["network", "ssh", "exposure"]
        )
        
    def supports(self, node_type: str) -> bool:
        return node_type == "SecurityGroup"
        
    def compliance(self) -> List[ComplianceFramework]: 
        return [ComplianceFramework.CIS, ComplianceFramework.SOC2, ComplianceFramework.PCI_DSS]
        
    def validate(self) -> bool: return True
    
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        node = graph.get_node(node_id)
        inbound_rules = node.get("configuration", {}).get("inbound_rules", [])
        
        for rule in inbound_rules:
            port = rule.get("from_port")
            to_port = rule.get("to_port")
            ip_ranges = rule.get("ip_ranges", [])
            
            if port is not None and port <= 22 and to_port is not None and to_port >= 22:
                if "0.0.0.0/0" in ip_ranges:
                    evidence = Evidence(
                        resource_id=node_id,
                        resource_type="SecurityGroup",
                        expected="Restricted CIDR range",
                        actual="0.0.0.0/0",
                        reason="Inbound rule permits 0.0.0.0/0 on TCP port 22.",
                        property="inbound_rules",
                        raw_data=rule
                    )
                    return SecurityFinding(
                        rule_id=self.metadata().id,
                        rule_name=self.metadata().name,
                        resource_id=node_id,
                        resource_type="SecurityGroup",
                        category=self.metadata().category,
                        base_severity=self.metadata().severity,
                        description=self.metadata().description,
                        root_cause="Open network exposure on management port.",
                        technical_impact="Attackers can brute-force SSH credentials across the internet.",
                        business_impact="Unauthorized server access and potential data exfiltration.",
                        recommendation="Restrict SSH access to a specific corporate IP range or Bastion Host.",
                        compliance_mapping=self.compliance(),
                        evidence=evidence,
                        automation_possible=True
                    )
        return None
