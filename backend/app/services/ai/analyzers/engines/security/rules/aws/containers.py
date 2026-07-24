"""
Container Security Rules.
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

class ContainerBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool: return True

# EKS
class EKSPublicEndpointRule(ContainerBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EKS-001", version="1.0.0", name="EKS Public Endpoint Enabled", description="Cluster endpoint is public.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.KUBERNETES, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["EKS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "EKS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        vpc = config.get("resources_vpc_config", {})
        if vpc.get("endpoint_public_access", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EKS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Public access enabled.", technical_impact="Control plane is internet accessible.", business_impact="Cluster compromise risk.",
                recommendation="Disable public access.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="EKS", expected=False, actual=True, reason="Endpoint public access is true.", property="resources_vpc_config.endpoint_public_access", raw_data=config)
            )
        return None

class EKSAuditLogsDisabledRule(ContainerBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EKS-002", version="1.0.0", name="EKS Audit Logs Disabled", description="Audit logs not sent to CloudWatch.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.LOGGING, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["EKS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.SOC2])
    def supports(self, node_type: str) -> bool: return node_type == "EKS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        logs = config.get("logging", {}).get("cluster_logging", [])
        audit_enabled = False
        for lg in logs:
            if "audit" in lg.get("types", []) and lg.get("enabled"):
                audit_enabled = True
        if not audit_enabled:
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EKS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Audit logs off.", technical_impact="No visibility into k8s API calls.", business_impact="Compliance failure.",
                recommendation="Enable audit logging.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="EKS", expected=True, actual=False, reason="Audit logs not found in cluster_logging.", property="logging", raw_data=config)
            )
        return None

class EKSSecretsEncryptionRule(ContainerBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EKS-003", version="1.0.0", name="EKS Secrets Encryption Disabled", description="KMS encryption for secrets is missing.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.ENCRYPTION, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["EKS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "EKS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        enc_config = config.get("encryption_config", [])
        secrets_encrypted = False
        for ec in enc_config:
            if "secrets" in ec.get("resources", []):
                secrets_encrypted = True
        if not secrets_encrypted:
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EKS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Secrets encryption off.", technical_impact="etcd stores secrets in plaintext.", business_impact="Data breach.",
                recommendation="Enable envelope encryption for secrets.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="EKS", expected=True, actual=False, reason="Secrets missing from encryption_config.", property="encryption_config", raw_data=config)
            )
        return None

class EKSPrivateEndpointDisabledRule(ContainerBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-EKS-004", version="1.0.0", name="EKS Endpoint Private Access Disabled", description="Private endpoint is disabled.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.KUBERNETES, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["EKS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "EKS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        vpc = config.get("resources_vpc_config", {})
        if not vpc.get("endpoint_private_access", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="EKS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Private access disabled.", technical_impact="Nodes communicate over public internet.", business_impact="Increased attack surface.",
                recommendation="Enable private endpoint access.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="EKS", expected=True, actual=False, reason="Endpoint private access is false.", property="resources_vpc_config.endpoint_private_access", raw_data=config)
            )
        return None

# ECS
class ECSPrivilegedContainerRule(ContainerBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-ECS-001", version="1.0.0", name="ECS Privileged Container", description="Container runs as privileged.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.CONTAINERS, capability=RuleCapability.DETECTIVE, severity=Severity.CRITICAL, resource_types=["ECSTaskDefinition"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "ECSTaskDefinition"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        for container in config.get("container_definitions", []):
            if container.get("privileged", False):
                return SecurityFinding(
                    rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="ECSTaskDefinition", category=self.metadata().category, base_severity=self.metadata().severity,
                    description=self.metadata().description, root_cause="Privileged flag true.", technical_impact="Container escape.", business_impact="Host compromise.",
                    recommendation="Remove privileged flag.", compliance_mapping=self.compliance(),
                    evidence=Evidence(resource_id=node_id, resource_type="ECSTaskDefinition", expected=False, actual=True, reason="Container is privileged.", property="container_definitions.privileged", raw_data=container)
                )
        return None

class ECSLatestTagRule(ContainerBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-ECS-002", version="1.0.0", name="ECS Latest Tag Used", description="Container uses latest tag.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.CONTAINERS, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["ECSTaskDefinition"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "ECSTaskDefinition"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        for container in config.get("container_definitions", []):
            image = container.get("image", "")
            if ":latest" in image or ":" not in image:
                return SecurityFinding(
                    rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="ECSTaskDefinition", category=self.metadata().category, base_severity=self.metadata().severity,
                    description=self.metadata().description, root_cause="Latest tag used.", technical_impact="Unpredictable deployments.", business_impact="Availability risk.",
                    recommendation="Use specific image digests or version tags.", compliance_mapping=self.compliance(),
                    evidence=Evidence(resource_id=node_id, resource_type="ECSTaskDefinition", expected="Specific Tag", actual=image, reason="Latest tag found.", property="container_definitions.image", raw_data=container)
                )
        return None

class ECSTaskRoleMissingRule(ContainerBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-ECS-003", version="1.0.0", name="ECS Task Role Missing", description="Task execution role missing.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["ECSTaskDefinition"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "ECSTaskDefinition"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("task_role_arn"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="ECSTaskDefinition", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Task role missing.", technical_impact="Containers use host EC2 instance role.", business_impact="Privilege escalation.",
                recommendation="Assign specific task roles.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="ECSTaskDefinition", expected="ARN Configured", actual=None, reason="Task Role ARN missing.", property="task_role_arn", raw_data=config)
            )
        return None

# ECR
class ECRImageScanRule(ContainerBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-ECR-001", version="1.0.0", name="ECR Image Scan Disabled", description="Scan on push disabled.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.CONTAINERS, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["ECR"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "ECR"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        scan_config = config.get("image_scanning_configuration", {})
        if not scan_config.get("scan_on_push", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="ECR", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Scan on push disabled.", technical_impact="Vulnerable images can be deployed.", business_impact="Security breach.",
                recommendation="Enable scan on push.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="ECR", expected=True, actual=False, reason="Scan on push is false.", property="image_scanning_configuration", raw_data=config)
            )
        return None

class ECRImmutableTagsRule(ContainerBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-ECR-002", version="1.0.0", name="ECR Immutable Tags Disabled", description="Image tags are mutable.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.CONTAINERS, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["ECR"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.SOC2])
    def supports(self, node_type: str) -> bool: return node_type == "ECR"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("image_tag_mutability") != "IMMUTABLE":
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="ECR", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Tags are mutable.", technical_impact="Images can be silently overwritten.", business_impact="Supply chain attack.",
                recommendation="Set image tag mutability to IMMUTABLE.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="ECR", expected="IMMUTABLE", actual=config.get("image_tag_mutability"), reason="Tags are not immutable.", property="image_tag_mutability", raw_data=config)
            )
        return None


class ContainerRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            EKSPublicEndpointRule(), EKSAuditLogsDisabledRule(), EKSSecretsEncryptionRule(), EKSPrivateEndpointDisabledRule(),
            ECSPrivilegedContainerRule(), ECSLatestTagRule(), ECSTaskRoleMissingRule(),
            ECRImageScanRule(), ECRImmutableTagsRule()
        ]
