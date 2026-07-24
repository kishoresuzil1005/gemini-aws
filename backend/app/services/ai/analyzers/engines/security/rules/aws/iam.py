"""
IAM Security Rules.
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

class IAMBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool:
        return True

class IAMWildcardActionRule(IAMBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-IAM-001", version="1.0.0", name="IAM Policy allows Wildcard Actions", description="IAM Policy grants '*' permissions.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY,
            capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["IAMPolicy", "IAMRole", "IAMUser", "IAMGroup"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type in ["IAMPolicy", "IAMRole", "IAMUser", "IAMGroup"]
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        statements = config.get("policy_document", {}).get("Statement", [])
        if isinstance(statements, dict): statements = [statements]
        for statement in statements:
            if statement.get("Effect") == "Allow":
                actions = statement.get("Action", [])
                if isinstance(actions, str): actions = [actions]
                if "*" in actions or "iam:*" in actions:
                    return SecurityFinding(
                        rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type=graph.get_node(node_id).get("type", "IAM"), category=self.metadata().category, base_severity=self.metadata().severity,
                        description=self.metadata().description, root_cause="Wildcard used in Action block.", technical_impact="Privilege escalation.", business_impact="Complete account compromise.",
                        recommendation="Specify exact actions required.", compliance_mapping=self.compliance(),
                        evidence=Evidence(resource_id=node_id, resource_type=graph.get_node(node_id).get("type", "IAM"), expected="Specific Actions", actual="*", reason="Wildcard action found.", property="policy_document", raw_data=statement)
                    )
        return None

class IAMWildcardResourceRule(IAMBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-IAM-002", version="1.0.0", name="IAM Policy allows Wildcard Resources", description="IAM Policy applies to '*' resources.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["IAMPolicy"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "IAMPolicy"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        statements = config.get("policy_document", {}).get("Statement", [])
        if isinstance(statements, dict): statements = [statements]
        for statement in statements:
            if statement.get("Effect") == "Allow":
                resources = statement.get("Resource", [])
                if isinstance(resources, str): resources = [resources]
                if "*" in resources:
                    return SecurityFinding(
                        rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="IAMPolicy", category=self.metadata().category, base_severity=self.metadata().severity,
                        description=self.metadata().description, root_cause="Wildcard used in Resource block.", technical_impact="Policy grants access to all resources in account.", business_impact="Unintended exposure of sensitive assets.",
                        recommendation="Specify exact resource ARNs.", compliance_mapping=self.compliance(),
                        evidence=Evidence(resource_id=node_id, resource_type="IAMPolicy", expected="Specific ARNs", actual="*", reason="Wildcard resource found.", property="policy_document", raw_data=statement)
                    )
        return None

class IAMRootAccountUsageRule(IAMBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-IAM-003", version="1.0.0", name="Root Account Usage", description="Root account has been used recently.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY, capability=RuleCapability.DETECTIVE, severity=Severity.CRITICAL, resource_types=["AWSAccount"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "AWSAccount"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("root_account_used_recently"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="AWSAccount", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Root account active.", technical_impact="Risk of root credentials exposure.", business_impact="Complete account compromise.",
                recommendation="Do not use the root account for daily tasks.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="AWSAccount", expected=False, actual=True, reason="Root account used recently.", property="root_account_used_recently", raw_data=config)
            )
        return None

class IAMMFADisabledRule(IAMBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-IAM-004", version="1.0.0", name="IAM User MFA Disabled", description="MFA is not enabled for IAM user.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["IAMUser"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "IAMUser"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("mfa_active", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="IAMUser", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="MFA not configured.", technical_impact="Credential theft leads to immediate access.", business_impact="Security breach.",
                recommendation="Enable MFA for the user.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="IAMUser", expected=True, actual=False, reason="MFA is not active.", property="mfa_active", raw_data=config)
            )
        return None

class IAMAdminPolicyRule(IAMBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-IAM-005", version="1.0.0", name="AdministratorAccess Policy Attached", description="AdministratorAccess is directly attached to a user.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["IAMUser"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "IAMUser"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        attached_policies = config.get("attached_policies", [])
        for policy in attached_policies:
            if "AdministratorAccess" in policy.get("policy_arn", ""):
                return SecurityFinding(
                    rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="IAMUser", category=self.metadata().category, base_severity=self.metadata().severity,
                    description=self.metadata().description, root_cause="Direct admin policy attachment.", technical_impact="User has unrestricted access.", business_impact="Excessive privilege risk.",
                    recommendation="Attach Admin policies to roles/groups instead of users directly.", compliance_mapping=self.compliance(),
                    evidence=Evidence(resource_id=node_id, resource_type="IAMUser", expected="No AdministratorAccess", actual="AdministratorAccess", reason="Admin policy attached directly.", property="attached_policies", raw_data=policy)
                )
        return None

class IAMInlinePoliciesRule(IAMBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-IAM-006", version="1.0.0", name="Inline Policies Attached", description="IAM User has inline policies attached.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["IAMUser"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "IAMUser"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("inline_policies"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="IAMUser", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Inline policies used.", technical_impact="Policies cannot be audited easily.", business_impact="Governance tracking issues.",
                recommendation="Use customer managed policies instead of inline policies.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="IAMUser", expected="0 inline policies", actual=len(config.get("inline_policies")), reason="User has inline policies.", property="inline_policies", raw_data=config)
            )
        return None

class IAMOldAccessKeysRule(IAMBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-IAM-007", version="1.0.0", name="Old Access Keys", description="Access keys older than 90 days.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["IAMUser"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "IAMUser"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        for key in config.get("access_keys", []):
            if key.get("age_days", 0) > 90:
                return SecurityFinding(
                    rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="IAMUser", category=self.metadata().category, base_severity=self.metadata().severity,
                    description=self.metadata().description, root_cause="Access key not rotated.", technical_impact="Risk of compromised key usage.", business_impact="Data breach.",
                    recommendation="Rotate access keys every 90 days.", compliance_mapping=self.compliance(),
                    evidence=Evidence(resource_id=node_id, resource_type="IAMUser", expected="< 90 days", actual=key.get("age_days"), reason="Key is older than 90 days.", property="access_keys", raw_data=key)
                )
        return None

class IAMUnusedCredentialsRule(IAMBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-IAM-008", version="1.0.0", name="Unused Credentials", description="Credentials unused for 90 days.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["IAMUser"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "IAMUser"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("password_last_used_days", 0) > 90:
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="IAMUser", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Dormant account.", technical_impact="Unmonitored access point.", business_impact="Unauthorized access.",
                recommendation="Disable unused credentials.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="IAMUser", expected="< 90 days", actual=config.get("password_last_used_days"), reason="Password unused for > 90 days.", property="password_last_used_days", raw_data=config)
            )
        return None

class IAMWeakPasswordPolicyRule(IAMBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-IAM-009", version="1.0.0", name="Weak Password Policy", description="Password policy lacks complexity requirements.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["AWSAccount"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS]
        )
    def supports(self, node_type: str) -> bool: return node_type == "AWSAccount"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        policy = config.get("password_policy", {})
        if not policy.get("require_symbols") or policy.get("minimum_password_length", 0) < 14:
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="AWSAccount", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Weak password requirements.", technical_impact="Brute force susceptibility.", business_impact="Account compromise.",
                recommendation="Enforce strong password policy (length >= 14, symbols, etc).", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="AWSAccount", expected="min_length >= 14, symbols=True", actual=policy, reason="Policy lacks complexity.", property="password_policy", raw_data=policy)
            )
        return None

class IAMAccessAnalyzerDisabledRule(IAMBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(
            id="AWS-IAM-010", version="1.0.0", name="Access Analyzer Disabled", description="IAM Access Analyzer is disabled.",
            provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.IDENTITY, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["AWSAccount"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED]
        )
    def supports(self, node_type: str) -> bool: return node_type == "AWSAccount"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("access_analyzer_enabled", False):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="AWSAccount", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Analyzer disabled.", technical_impact="Cannot proactively detect external access.", business_impact="Unintended exposure.",
                recommendation="Enable IAM Access Analyzer.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="AWSAccount", expected=True, actual=False, reason="Access analyzer not enabled.", property="access_analyzer_enabled", raw_data=config)
            )
        return None


class IAMRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            IAMWildcardActionRule(),
            IAMWildcardResourceRule(),
            IAMRootAccountUsageRule(),
            IAMMFADisabledRule(),
            IAMAdminPolicyRule(),
            IAMInlinePoliciesRule(),
            IAMOldAccessKeysRule(),
            IAMUnusedCredentialsRule(),
            IAMWeakPasswordPolicyRule(),
            IAMAccessAnalyzerDisabledRule()
        ]
