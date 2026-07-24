"""
RDS Security Rules.
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

class RDSBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool:
        return True

class RDSPublicAccessRule(RDSBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-RDS-001", version="1.0.0", name="RDS Public Database", description="RDS instance is Publicly Accessible.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.DATABASE, capability=RuleCapability.DETECTIVE, severity=Severity.CRITICAL, resource_types=["RDS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS, ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "RDS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("publicly_accessible", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="RDS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="PubliclyAccessible is True.", technical_impact="DB port exposed.", business_impact="Data breach.",
                recommendation="Set PubliclyAccessible to False.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="RDS", expected=False, actual=True, reason="Public routing enabled.", property="publicly_accessible", raw_data=config)
            )
        return None

class RDSEncryptionRule(RDSBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-RDS-002", version="1.0.0", name="RDS Encryption Disabled", description="RDS instance is not encrypted.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.ENCRYPTION, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["RDS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS, ComplianceFramework.SOC2, ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "RDS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("storage_encrypted", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="RDS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Storage is not encrypted.", technical_impact="Data in plaintext on disk.", business_impact="Compliance failure.",
                recommendation="Enable storage encryption.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="RDS", expected=True, actual=False, reason="Encryption disabled.", property="storage_encrypted", raw_data=config)
            )
        return None

class RDSBackupDisabledRule(RDSBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-RDS-003", version="1.0.0", name="RDS Backup Disabled", description="RDS automatic backups disabled.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.DATABASE, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["RDS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.SOC2])
    def supports(self, node_type: str) -> bool: return node_type == "RDS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("backup_retention_period", 0) == 0:
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="RDS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Backup retention is 0.", technical_impact="No automated recovery.", business_impact="Data loss.",
                recommendation="Set backup retention to > 0.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="RDS", expected="> 0", actual=0, reason="Backups disabled.", property="backup_retention_period", raw_data=config)
            )
        return None

class RDSMultiAZRule(RDSBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-RDS-004", version="1.0.0", name="RDS MultiAZ Disabled", description="RDS instance lacks Multi-AZ.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.RESILIENCE, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["RDS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.SOC2])
    def supports(self, node_type: str) -> bool: return node_type == "RDS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("multi_az", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="RDS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Multi-AZ disabled.", technical_impact="Single point of failure.", business_impact="Downtime during AZ outages.",
                recommendation="Enable Multi-AZ.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="RDS", expected=True, actual=False, reason="Not highly available.", property="multi_az", raw_data=config)
            )
        return None

class RDSDeletionProtectionRule(RDSBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-RDS-005", version="1.0.0", name="RDS Deletion Protection Disabled", description="Deletion protection is disabled.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.DATABASE, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["RDS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.SOC2])
    def supports(self, node_type: str) -> bool: return node_type == "RDS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("deletion_protection", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="RDS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Deletion protection off.", technical_impact="Accidental database termination possible.", business_impact="Catastrophic data loss.",
                recommendation="Enable deletion protection.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="RDS", expected=True, actual=False, reason="Not protected.", property="deletion_protection", raw_data=config)
            )
        return None

class RDSPerformanceInsightsRule(RDSBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-RDS-006", version="1.0.0", name="RDS Performance Insights Disabled", description="Performance Insights disabled.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.MONITORING, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["RDS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "RDS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("performance_insights_enabled", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="RDS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Performance Insights off.", technical_impact="Reduced observability.", business_impact="Slow troubleshooting.",
                recommendation="Enable Performance Insights.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="RDS", expected=True, actual=False, reason="Insights disabled.", property="performance_insights_enabled", raw_data=config)
            )
        return None

class RDSOldEngineRule(RDSBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-RDS-007", version="1.0.0", name="RDS Old Engine Version", description="RDS using an outdated engine version.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.DATABASE, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["RDS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "RDS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        version = config.get("engine_version", "")
        # Dummy check for old version (deterministic fallback)
        if version.startswith("5.6"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="RDS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Old engine used.", technical_impact="Missing security patches.", business_impact="Exploitation risk.",
                recommendation="Upgrade database engine.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="RDS", expected="Modern version", actual=version, reason="Engine version is outdated.", property="engine_version", raw_data=config)
            )
        return None

class RDSAutoMinorVersionUpgradeRule(RDSBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-RDS-008", version="1.0.0", name="RDS Auto Minor Version Upgrade Disabled", description="Auto minor version upgrade is disabled.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.DATABASE, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["RDS"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "RDS"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("auto_minor_version_upgrade", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="RDS", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Auto upgrade disabled.", technical_impact="Missing automatic security patches.", business_impact="Vulnerability accumulation.",
                recommendation="Enable auto minor version upgrade.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="RDS", expected=True, actual=False, reason="Auto upgrade not enabled.", property="auto_minor_version_upgrade", raw_data=config)
            )
        return None

class RDSRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            RDSPublicAccessRule(), RDSEncryptionRule(), RDSBackupDisabledRule(), RDSMultiAZRule(),
            RDSDeletionProtectionRule(), RDSPerformanceInsightsRule(), RDSOldEngineRule(), RDSAutoMinorVersionUpgradeRule()
        ]
