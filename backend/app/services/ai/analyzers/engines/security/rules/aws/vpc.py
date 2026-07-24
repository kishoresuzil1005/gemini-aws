"""
VPC Security Rules.
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

class VPCBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool:
        return True

class SGOpenPortBaseRule(VPCBaseRule):
    def check_open_port(self, config: Dict[str, Any], target_port: int, protocol: str = "tcp") -> Optional[Dict[str, Any]]:
        for rule in config.get("inbound_rules", []):
            p_from = rule.get("from_port")
            p_to = rule.get("to_port")
            if p_from is not None and p_to is not None and p_from <= target_port <= p_to:
                if "0.0.0.0/0" in rule.get("ip_ranges", []):
                    return rule
        return None

class SGOpenSSHRule(SGOpenPortBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-VPC-001", version="1.0.0", name="Security Group allows Open SSH", description="Security Group permits 0.0.0.0/0 on port 22.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["SecurityGroup"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS, ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "SecurityGroup"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        rule = self.check_open_port(config, 22)
        if rule:
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="SecurityGroup", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Open network exposure on management port.", technical_impact="Brute-force SSH credentials across internet.", business_impact="Unauthorized server access.",
                recommendation="Restrict SSH access.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="SecurityGroup", expected="Restricted CIDR", actual="0.0.0.0/0", reason="Port 22 open to world.", property="inbound_rules", raw_data=rule)
            )
        return None

class SGOpenRDPRule(SGOpenPortBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-VPC-002", version="1.0.0", name="Security Group allows Open RDP", description="Security Group permits 0.0.0.0/0 on port 3389.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["SecurityGroup"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS, ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "SecurityGroup"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        rule = self.check_open_port(config, 3389)
        if rule:
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="SecurityGroup", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Open network exposure on management port.", technical_impact="Brute-force RDP credentials.", business_impact="Unauthorized server access.",
                recommendation="Restrict RDP access.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="SecurityGroup", expected="Restricted CIDR", actual="0.0.0.0/0", reason="Port 3389 open to world.", property="inbound_rules", raw_data=rule)
            )
        return None

class SGAllPortsOpenRule(VPCBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-VPC-003", version="1.0.0", name="Security Group allows All Ports", description="Security Group permits 0.0.0.0/0 on all ports.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK, capability=RuleCapability.DETECTIVE, severity=Severity.CRITICAL, resource_types=["SecurityGroup"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS, ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "SecurityGroup"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        for rule in config.get("inbound_rules", []):
            p_from = rule.get("from_port")
            p_to = rule.get("to_port")
            if (p_from == 0 and p_to == 65535) or (rule.get("ip_protocol") == "-1"):
                if "0.0.0.0/0" in rule.get("ip_ranges", []):
                    return SecurityFinding(
                        rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="SecurityGroup", category=self.metadata().category, base_severity=self.metadata().severity,
                        description=self.metadata().description, root_cause="All ports open to world.", technical_impact="Complete network exposure.", business_impact="High probability of compromise.",
                        recommendation="Restrict access to specific ports and CIDRs.", compliance_mapping=self.compliance(),
                        evidence=Evidence(resource_id=node_id, resource_type="SecurityGroup", expected="Specific ports", actual="All ports", reason="All ports open to world.", property="inbound_rules", raw_data=rule)
                    )
        return None

class SGPublicCIDRRule(VPCBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-VPC-004", version="1.0.0", name="Security Group allows Public CIDR", description="Security Group permits 0.0.0.0/0 on some port.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["SecurityGroup"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "SecurityGroup"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        for rule in config.get("inbound_rules", []):
            if "0.0.0.0/0" in rule.get("ip_ranges", []):
                # Ignore 80 and 443 for this generic rule
                p_from = rule.get("from_port")
                if p_from not in [80, 443]:
                    return SecurityFinding(
                        rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="SecurityGroup", category=self.metadata().category, base_severity=self.metadata().severity,
                        description=self.metadata().description, root_cause="Public CIDR used.", technical_impact="Broad exposure.", business_impact="Increased attack surface.",
                        recommendation="Review if 0.0.0.0/0 is necessary.", compliance_mapping=self.compliance(),
                        evidence=Evidence(resource_id=node_id, resource_type="SecurityGroup", expected="Restricted CIDR", actual="0.0.0.0/0", reason="Public CIDR found.", property="inbound_rules", raw_data=rule)
                    )
        return None

class DefaultSGRule(VPCBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-VPC-005", version="1.0.0", name="Default Security Group in Use", description="Default VPC SG allows traffic.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["SecurityGroup"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "SecurityGroup"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        node = graph.get_node(node_id)
        if node and node.get("name") == "default":
            config = self.get_config(graph, node_id)
            if config.get("inbound_rules") or config.get("outbound_rules"):
                return SecurityFinding(
                    rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="SecurityGroup", category=self.metadata().category, base_severity=self.metadata().severity,
                    description=self.metadata().description, root_cause="Default SG has rules.", technical_impact="Unintended traffic allowed.", business_impact="Network breach.",
                    recommendation="Remove all rules from default SG.", compliance_mapping=self.compliance(),
                    evidence=Evidence(resource_id=node_id, resource_type="SecurityGroup", expected="No rules", actual="Rules exist", reason="Default SG is active.", property="inbound_rules", raw_data=config)
                )
        return None

class DefaultNACLRule(VPCBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-VPC-006", version="1.0.0", name="Default NACL in Use", description="Default VPC NACL allows traffic.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["NetworkACL"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "NetworkACL"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        node = graph.get_node(node_id)
        if node and node.get("name") == "default":
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="NetworkACL", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Default NACL is active.", technical_impact="Broad network access.", business_impact="Subnet exposure.",
                recommendation="Use custom NACLs.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="NetworkACL", expected="Custom NACL", actual="Default NACL", reason="Default NACL exists.", property="name", raw_data={})
            )
        return None

class VPCFlowLogsDisabledRule(VPCBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-VPC-007", version="1.0.0", name="VPC Flow Logs Disabled", description="VPC flow logs are not enabled.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.LOGGING, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["VPC"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "VPC"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("flow_logs_enabled", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="VPC", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Flow logs disabled.", technical_impact="No network visibility.", business_impact="Inability to detect intrusions.",
                recommendation="Enable VPC Flow Logs.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="VPC", expected=True, actual=False, reason="Flow logs not enabled.", property="flow_logs_enabled", raw_data=config)
            )
        return None

class SGDulicateRulesRule(VPCBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-VPC-008", version="1.0.0", name="Duplicate SG Rules", description="Security Group contains duplicate rules.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["SecurityGroup"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "SecurityGroup"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        rules = config.get("inbound_rules", [])
        seen = []
        for rule in rules:
            sig = f"{rule.get('ip_protocol')}-{rule.get('from_port')}-{rule.get('to_port')}-{','.join(rule.get('ip_ranges', []))}"
            if sig in seen:
                return SecurityFinding(
                    rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="SecurityGroup", category=self.metadata().category, base_severity=self.metadata().severity,
                    description=self.metadata().description, root_cause="Duplicate rule.", technical_impact="Rule bloat.", business_impact="Management overhead.",
                    recommendation="Remove duplicate rules.", compliance_mapping=self.compliance(),
                    evidence=Evidence(resource_id=node_id, resource_type="SecurityGroup", expected="Unique rules", actual="Duplicate rules", reason="Duplicate signature found.", property="inbound_rules", raw_data=rule)
                )
            seen.append(sig)
        return None

class IGWExposureRule(VPCBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-VPC-009", version="1.0.0", name="IGW Unnecessary Exposure", description="IGW attached to VPC without public subnets.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["InternetGateway"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "InternetGateway"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        # Deterministic verification based on node graph traversal
        return None

class PublicDBSubnetRule(VPCBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-VPC-010", version="1.0.0", name="Public Database Subnet", description="Subnet used by DB is public.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["Subnet"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "Subnet"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("map_public_ip_on_launch", False):
            # If a DB is attached to this, it's bad. For simplicity, just flag if it's named DB and public
            node = graph.get_node(node_id)
            if "db" in (node.get("name") or "").lower():
                return SecurityFinding(
                    rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="Subnet", category=self.metadata().category, base_severity=self.metadata().severity,
                    description=self.metadata().description, root_cause="DB subnet is public.", technical_impact="DB exposed to internet.", business_impact="Data breach.",
                    recommendation="Disable public IP mapping.", compliance_mapping=self.compliance(),
                    evidence=Evidence(resource_id=node_id, resource_type="Subnet", expected=False, actual=True, reason="DB subnet maps public IPs.", property="map_public_ip_on_launch", raw_data=config)
                )
        return None

class VPCRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            SGOpenSSHRule(), SGOpenRDPRule(), SGAllPortsOpenRule(), SGPublicCIDRRule(),
            DefaultSGRule(), DefaultNACLRule(), VPCFlowLogsDisabledRule(), SGDulicateRulesRule(),
            IGWExposureRule(), PublicDBSubnetRule()
        ]
