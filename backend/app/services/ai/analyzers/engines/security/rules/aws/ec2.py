"""
EC2 Security Rules.
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

class EC2BaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool: return True

class EC2PublicIPRule(EC2BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EC2-001", version="1.0.0", name="EC2 Public IP Assigned", description="EC2 instance has a public IP address.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["EC2"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "EC2"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("public_ip_address"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EC2", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Instance provisioned in public subnet with public IP.", technical_impact="Directly addressable from internet.", business_impact="Exposure to internet scanning and attacks.",
                recommendation="Remove public IP and use a load balancer or bastion.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="EC2", expected=None, actual=config.get("public_ip_address"), reason="Public IP found.", property="public_ip_address", raw_data=config)
            )
        return None

class EC2IMDSv1Rule(EC2BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EC2-002", version="1.0.0", name="EC2 IMDSv1 Enabled", description="Instance Metadata Service v1 is enabled.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.COMPUTE, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["EC2"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "EC2"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        metadata_options = config.get("metadata_options", {})
        if metadata_options.get("http_tokens") != "required":
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EC2", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="IMDSv2 not enforced.", technical_impact="SSRF attacks can extract instance credentials.", business_impact="Data breach.",
                recommendation="Require IMDSv2 by setting HttpTokens to required.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="EC2", expected="required", actual=metadata_options.get("http_tokens"), reason="Tokens are not required.", property="metadata_options.http_tokens", raw_data=config)
            )
        return None

class EC2MonitoringRule(EC2BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EC2-003", version="1.0.0", name="EC2 Detailed Monitoring Disabled", description="Detailed monitoring is off.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.MONITORING, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["EC2"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "EC2"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        monitoring = config.get("monitoring", {})
        if monitoring.get("state") != "enabled":
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EC2", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Detailed monitoring not enabled.", technical_impact="Slower response to incidents.", business_impact="Delayed troubleshooting.",
                recommendation="Enable detailed monitoring.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="EC2", expected="enabled", actual=monitoring.get("state"), reason="Monitoring is not enabled.", property="monitoring.state", raw_data=config)
            )
        return None

class EC2NoIAMRoleRule(EC2BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EC2-004", version="1.0.0", name="EC2 No IAM Role", description="EC2 instance has no IAM role attached.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["EC2"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "EC2"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("iam_instance_profile"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EC2", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="No IAM profile.", technical_impact="Applications might use hardcoded credentials.", business_impact="Credential leakage.",
                recommendation="Attach an IAM instance profile.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="EC2", expected="Profile Configured", actual=None, reason="IAM profile is missing.", property="iam_instance_profile", raw_data=config)
            )
        return None

class EC2TerminationProtectionRule(EC2BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EC2-005", version="1.0.0", name="EC2 Termination Protection Disabled", description="Termination protection is disabled.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.RESILIENCE, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["EC2"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.SOC2])
    def supports(self, node_type: str) -> bool: return node_type == "EC2"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("disable_api_termination", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EC2", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="API termination allowed.", technical_impact="Instance can be accidentally terminated.", business_impact="Service disruption.",
                recommendation="Enable termination protection.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="EC2", expected=True, actual=False, reason="Termination protection is false.", property="disable_api_termination", raw_data=config)
            )
        return None

class EC2OldFamilyRule(EC2BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EC2-006", version="1.0.0", name="EC2 Old Instance Family", description="Using previous generation instance types.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.COMPUTE, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["EC2"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "EC2"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        instance_type = config.get("instance_type", "")
        if instance_type.startswith("t2.") or instance_type.startswith("m3."):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EC2", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Old generation type used.", technical_impact="Missing Nitro security features.", business_impact="Lower performance and security.",
                recommendation="Upgrade to current generation (e.g. t3, m5).", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="EC2", expected="Modern Generation", actual=instance_type, reason="Old instance type detected.", property="instance_type", raw_data=config)
            )
        return None

class EC2RootVolumeEncryptedRule(EC2BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EC2-007", version="1.0.0", name="EC2 Root Volume Not Encrypted", description="Root EBS volume is unencrypted.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.ENCRYPTION, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["EC2"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS, ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "EC2"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        mappings = config.get("block_device_mappings", [])
        for mapping in mappings:
            ebs = mapping.get("ebs", {})
            if not ebs.get("encrypted", False):
                return SecurityFinding(
                    rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EC2", category=self.metadata().category, base_severity=self.metadata().severity,
                    description=self.metadata().description, root_cause="EBS encryption disabled.", technical_impact="Data at rest is plaintext.", business_impact="Compliance violation.",
                    recommendation="Enable EBS encryption.", compliance_mapping=self.compliance(),
                    evidence=Evidence(resource_id=node_id, resource_type="EC2", expected=True, actual=False, reason="Volume is not encrypted.", property="block_device_mappings.ebs.encrypted", raw_data=mapping)
                )
        return None

class EC2StoppedInstanceRule(EC2BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EC2-008", version="1.0.0", name="EC2 Stopped Instance Older Than Threshold", description="Instance is stopped for a long time.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.COMPUTE, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["EC2"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "EC2"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("state", {}).get("name") == "stopped":
            # For simplicity without date parsing in deterministic offline
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EC2", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Instance is stopped.", technical_impact="Unused resources.", business_impact="Cost overhead.",
                recommendation="Review and terminate stopped instances.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="EC2", expected="running", actual="stopped", reason="Instance is stopped.", property="state.name", raw_data=config)
            )
        return None

class EC2PublicAMIRule(EC2BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EC2-009", version="1.0.0", name="EC2 Public AMI", description="AMI is publicly accessible.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.COMPUTE, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["AMI"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "AMI"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("public", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="AMI", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="AMI marked public.", technical_impact="Anyone can boot this image.", business_impact="Data leakage.",
                recommendation="Make AMI private.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="AMI", expected=False, actual=True, reason="AMI is public.", property="public", raw_data=config)
            )
        return None

class EC2RuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            EC2PublicIPRule(), EC2IMDSv1Rule(), EC2MonitoringRule(), EC2NoIAMRoleRule(),
            EC2TerminationProtectionRule(), EC2OldFamilyRule(), EC2RootVolumeEncryptedRule(),
            EC2StoppedInstanceRule(), EC2PublicAMIRule()
        ]
