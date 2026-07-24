"""
S3 Security Rules.
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

class S3BaseRule(SecurityRule):
    """Base class for S3 rules to share helpers."""
    def supports(self, node_type: str) -> bool:
        return node_type == "S3Bucket"
        
    def validate(self) -> bool:
        return True
        
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}

class S3PublicBucketRule(S3BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-001", version="1.0.0",
            name="S3 Bucket Public Access Enabled",
            description="S3 bucket allows public access by not enabling Block Public Access.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.STORAGE,
            capability=RuleCapability.DETECTIVE, severity=Severity.CRITICAL,
            resource_types=["S3Bucket"], supported_clouds=[CloudProvider.AWS],
            frameworks=[ComplianceFramework.CIS, ComplianceFramework.PCI_DSS]
        )
    
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        pab = config.get("public_access_block", {})
        
        if not pab.get("block_public_acls", False) or not pab.get("block_public_policy", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name,
                resource_id=node_id, resource_type="S3Bucket", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description,
                root_cause="Block Public Access is disabled.",
                technical_impact="Unauthenticated users might read/write data.",
                business_impact="Data breach.",
                recommendation="Enable Block Public Access for the bucket.",
                compliance_mapping=self.compliance(),
                evidence=Evidence(
                    resource_id=node_id, resource_type="S3Bucket",
                    expected={"block_public_acls": True, "block_public_policy": True},
                    actual={"block_public_acls": pab.get("block_public_acls"), "block_public_policy": pab.get("block_public_policy")},
                    reason="Public Access Block flags are missing or false.", property="public_access_block", raw_data=pab
                )
            )
        return None

class S3EncryptionDisabledRule(S3BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-002", version="1.0.0",
            name="S3 Encryption Disabled",
            description="S3 bucket does not enforce server-side encryption.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.ENCRYPTION,
            capability=RuleCapability.DETECTIVE, severity=Severity.HIGH,
            resource_types=["S3Bucket"], supported_clouds=[CloudProvider.AWS],
            frameworks=[ComplianceFramework.CIS, ComplianceFramework.SOC2, ComplianceFramework.PCI_DSS]
        )
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        enc = config.get("server_side_encryption", {})
        if not enc.get("enabled", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="S3Bucket", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Encryption at rest is not configured.", technical_impact="Data is stored in plaintext.", business_impact="Compliance violation.",
                recommendation="Enable default encryption using AWS KMS or Amazon S3 managed keys.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="S3Bucket", expected={"enabled": True}, actual={"enabled": enc.get("enabled")}, reason="Server-Side Encryption is disabled.", property="server_side_encryption", raw_data=enc)
            )
        return None

class S3VersioningDisabledRule(S3BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-003", version="1.0.0", name="S3 Versioning Disabled", description="S3 versioning is disabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.STORAGE,
            capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["S3Bucket"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.SOC2]
        )
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        ver = config.get("versioning", {})
        if ver.get("status") != "Enabled":
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="S3Bucket", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Versioning is not enabled.", technical_impact="Objects cannot be recovered if accidentally deleted.", business_impact="Data loss risk.",
                recommendation="Enable versioning.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="S3Bucket", expected="Enabled", actual=ver.get("status"), reason="Versioning status is not Enabled.", property="versioning.status", raw_data=ver)
            )
        return None

class S3AccessLoggingDisabledRule(S3BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-004", version="1.0.0", name="S3 Access Logging Disabled", description="S3 bucket access logging is disabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.LOGGING,
            capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["S3Bucket"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        logging = config.get("server_access_logging", {})
        if not logging.get("target_bucket"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="S3Bucket", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Server access logging is not configured.", technical_impact="No audit trail for object access.", business_impact="Inability to investigate data breaches.",
                recommendation="Enable server access logging.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="S3Bucket", expected="target_bucket configured", actual=None, reason="Target bucket is missing.", property="server_access_logging", raw_data=logging)
            )
        return None

class S3PublicACLRule(S3BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-005", version="1.0.0", name="S3 Public ACL", description="S3 bucket has a public Access Control List.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY,
            capability=RuleCapability.DETECTIVE, severity=Severity.CRITICAL, resource_types=["S3Bucket"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.PCI_DSS]
        )
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        grants = config.get("acl", {}).get("Grants", [])
        for grant in grants:
            grantee = grant.get("Grantee", {})
            uri = grantee.get("URI", "")
            if "AllUsers" in uri or "AuthenticatedUsers" in uri:
                return SecurityFinding(
                    rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="S3Bucket", category=self.metadata().category, base_severity=self.metadata().severity,
                    description=self.metadata().description, root_cause="Bucket ACL grants access to AllUsers.", technical_impact="Public exposure.", business_impact="Data breach.",
                    recommendation="Remove public grants from bucket ACL.", compliance_mapping=self.compliance(),
                    evidence=Evidence(resource_id=node_id, resource_type="S3Bucket", expected="No public URI", actual=uri, reason="ACL Grantee URI contains AllUsers.", property="acl.Grants", raw_data=grant)
                )
        return None

class S3BucketPolicyTooPermissiveRule(S3BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-006", version="1.0.0", name="S3 Bucket Policy Too Permissive", description="S3 bucket policy allows * principal.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY,
            capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["S3Bucket"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        policy = config.get("policy", {})
        statements = policy.get("Statement", [])
        if isinstance(statements, dict): statements = [statements]
        for statement in statements:
            if statement.get("Effect") == "Allow":
                principal = statement.get("Principal", "")
                if principal == "*" or (isinstance(principal, dict) and principal.get("AWS") == "*"):
                    return SecurityFinding(
                        rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="S3Bucket", category=self.metadata().category, base_severity=self.metadata().severity,
                        description=self.metadata().description, root_cause="Bucket policy contains Principal: *.", technical_impact="Public exposure.", business_impact="Data breach.",
                        recommendation="Remove * principal from bucket policy.", compliance_mapping=self.compliance(),
                        evidence=Evidence(resource_id=node_id, resource_type="S3Bucket", expected="Specific Principal", actual="*", reason="Principal is set to *.", property="policy.Statement.Principal", raw_data=statement)
                    )
        return None

class S3ObjectLockDisabledRule(S3BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-007", version="1.0.0", name="S3 Object Lock Disabled", description="S3 Object Lock is not enabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.STORAGE,
            capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["S3Bucket"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.SOC2]
        )
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("object_lock_enabled_for_bucket") is not True:
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="S3Bucket", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Object Lock is disabled.", technical_impact="Objects can be overwritten or deleted.", business_impact="Ransomware risk.",
                recommendation="Enable Object Lock.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="S3Bucket", expected=True, actual=config.get("object_lock_enabled_for_bucket"), reason="Object Lock is not enabled.", property="object_lock_enabled_for_bucket", raw_data=config)
            )
        return None

class S3MFADeleteDisabledRule(S3BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-008", version="1.0.0", name="S3 MFA Delete Disabled", description="S3 MFA Delete is not enabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.STORAGE,
            capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["S3Bucket"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        mfa_delete = config.get("versioning", {}).get("mfa_delete", "Disabled")
        if mfa_delete != "Enabled":
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="S3Bucket", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="MFA Delete is disabled.", technical_impact="Objects can be deleted without MFA.", business_impact="Accidental data loss.",
                recommendation="Enable MFA Delete.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="S3Bucket", expected="Enabled", actual=mfa_delete, reason="MFA Delete is not Enabled.", property="versioning.mfa_delete", raw_data=config)
            )
        return None

class S3LifecyclePolicyMissingRule(S3BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-009", version="1.0.0", name="S3 Lifecycle Policy Missing", description="S3 bucket has no lifecycle policies.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.STORAGE,
            capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["S3Bucket"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.SOC2]
        )
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("lifecycle_rules"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="S3Bucket", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="No lifecycle rules configured.", technical_impact="Stale data is retained forever.", business_impact="Unnecessary storage costs.",
                recommendation="Create a lifecycle policy.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="S3Bucket", expected="Configured rules", actual=None, reason="Lifecycle rules missing.", property="lifecycle_rules", raw_data=config)
            )
        return None

class S3BucketKeyDisabledRule(S3BaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-S3-010", version="1.0.0", name="S3 Bucket Key Disabled", description="S3 Bucket Key for KMS is disabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.ENCRYPTION,
            capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["S3Bucket"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED]
        )
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        bucket_key_enabled = config.get("server_side_encryption", {}).get("bucket_key_enabled", False)
        if not bucket_key_enabled:
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="S3Bucket", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Bucket Key is disabled.", technical_impact="Higher KMS request rates.", business_impact="Increased encryption costs.",
                recommendation="Enable S3 Bucket Key.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="S3Bucket", expected=True, actual=bucket_key_enabled, reason="Bucket Key is false.", property="server_side_encryption.bucket_key_enabled", raw_data=config)
            )
        return None


class S3RuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            S3PublicBucketRule(),
            S3EncryptionDisabledRule(),
            S3VersioningDisabledRule(),
            S3AccessLoggingDisabledRule(),
            S3PublicACLRule(),
            S3BucketPolicyTooPermissiveRule(),
            S3ObjectLockDisabledRule(),
            S3MFADeleteDisabledRule(),
            S3LifecyclePolicyMissingRule(),
            S3BucketKeyDisabledRule()
        ]
