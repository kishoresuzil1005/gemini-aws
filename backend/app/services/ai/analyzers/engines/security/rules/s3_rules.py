"""
S3 Security Rules.
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

class S3PublicAccessRule(SecurityRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-001",
            version="1.0.0",
            name="S3 Bucket Public Access Enabled",
            description="S3 bucket allows public read or write access.",
            provider=CloudProvider.AWS,
            domain=SecurityDomain.AWS,
            category=SecurityCategory.STORAGE,
            capability=RuleCapability.DETECTIVE,
            severity=Severity.CRITICAL,
            status=RuleStatus.ENABLED,
            created_version="1.0.0",
            tags=["s3", "public-access"],
            references=["CIS 2.1.1"]
        )
        
    def supports(self, node_type: str) -> bool:
        return node_type == "S3Bucket"
        
    def compliance(self) -> List[ComplianceFramework]: 
        return [ComplianceFramework.CIS, ComplianceFramework.PCI_DSS]
        
    def validate(self) -> bool:
        return True
    
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        node = graph.get_node(node_id)
        config = node.get("configuration", {})
        public_access_block = config.get("public_access_block", {})
        
        block_acls = public_access_block.get("block_public_acls", False)
        block_policy = public_access_block.get("block_public_policy", False)
        
        if not block_acls or not block_policy:
            evidence = Evidence(
                resource_id=node_id,
                resource_type="S3Bucket",
                expected={"block_public_acls": True, "block_public_policy": True},
                actual={"block_public_acls": block_acls, "block_public_policy": block_policy},
                reason="Public Access Block is disabled at the bucket level.",
                property="public_access_block",
                raw_data=public_access_block
            )
            
            return SecurityFinding(
                rule_id=self.metadata().id,
                rule_name=self.metadata().name,
                resource_id=node_id,
                resource_type="S3Bucket",
                category=self.metadata().category,
                base_severity=self.metadata().severity,
                description=self.metadata().description,
                root_cause="Public Access Block is not fully enforced.",
                technical_impact="Data exfiltration or unauthorized object mutation.",
                business_impact="Data breach leading to severe reputational and financial damage.",
                recommendation="Enable 'Block all public access' on the S3 bucket.",
                compliance_mapping=self.compliance(),
                evidence=evidence,
                automation_possible=True
            )
        return None

class S3EncryptionRule(SecurityRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-002",
            version="1.0.0",
            name="S3 Bucket Encryption Disabled",
            description="S3 bucket does not enforce server-side encryption.",
            provider=CloudProvider.AWS,
            domain=SecurityDomain.AWS,
            category=SecurityCategory.ENCRYPTION,
            capability=RuleCapability.DETECTIVE,
            severity=Severity.HIGH,
            status=RuleStatus.ENABLED,
            created_version="1.0.0",
            tags=["s3", "encryption", "data-at-rest"]
        )
        
    def supports(self, node_type: str) -> bool:
        return node_type == "S3Bucket"
        
    def compliance(self) -> List[ComplianceFramework]: 
        return [ComplianceFramework.CIS, ComplianceFramework.SOC2, ComplianceFramework.PCI_DSS]
        
    def validate(self) -> bool: return True
    
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        node = graph.get_node(node_id)
        config = node.get("configuration", {})
        encryption = config.get("server_side_encryption", {})
        
        is_enabled = encryption.get("enabled", False)
        
        if not is_enabled:
            evidence = Evidence(
                resource_id=node_id,
                resource_type="S3Bucket",
                expected={"enabled": True},
                actual={"enabled": False},
                reason="Server-Side Encryption is disabled.",
                property="server_side_encryption",
                raw_data=encryption
            )
            
            return SecurityFinding(
                rule_id=self.metadata().id,
                rule_name=self.metadata().name,
                resource_id=node_id,
                resource_type="S3Bucket",
                category=self.metadata().category,
                base_severity=self.metadata().severity,
                description=self.metadata().description,
                root_cause="Encryption at rest is not configured.",
                technical_impact="Compromised underlying storage exposes raw data.",
                business_impact="Compliance violation of data-at-rest encryption requirements.",
                recommendation="Enable default encryption using AWS KMS or Amazon S3 managed keys.",
                compliance_mapping=self.compliance(),
                evidence=evidence,
                automation_possible=True
            )
        return None
