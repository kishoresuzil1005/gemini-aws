"""
Lambda Security Rules.
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

class LambdaBaseRule(SecurityRule):
    def get_config(self, graph: InfrastructureGraph, node_id: str) -> Dict[str, Any]:
        node = graph.get_node(node_id)
        return node.get("configuration", {}) if node else {}
        
    def validate(self) -> bool: return True

class LambdaPublicInvokeRule(LambdaBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-LAMBDA-001", version="1.0.0", name="Lambda Public Invoke", description="Lambda allows public invocation.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.COMPUTE, capability=RuleCapability.DETECTIVE, severity=Severity.CRITICAL, resource_types=["Lambda"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "Lambda"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        policy = config.get("policy", {})
        for stmt in policy.get("Statement", []):
            if stmt.get("Effect") == "Allow" and stmt.get("Principal") == "*":
                return SecurityFinding(
                    rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="Lambda", category=self.metadata().category, base_severity=self.metadata().severity,
                    description=self.metadata().description, root_cause="Resource policy allows * principal.", technical_impact="Anyone can execute the function.", business_impact="Cost explosion and arbitrary code execution.",
                    recommendation="Remove * principal.", compliance_mapping=self.compliance(),
                    evidence=Evidence(resource_id=node_id, resource_type="Lambda", expected="Specific Principal", actual="*", reason="Public invoke allowed.", property="policy.Statement.Principal", raw_data=stmt)
                )
        return None

class LambdaEnvSecretsRule(LambdaBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-LAMBDA-002", version="1.0.0", name="Lambda Environment Secrets", description="Lambda environment contains secrets.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.SECRETS, capability=RuleCapability.DETECTIVE, severity=Severity.HIGH, resource_types=["Lambda"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.PCI_DSS])
    def supports(self, node_type: str) -> bool: return node_type == "Lambda"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        env = config.get("environment", {}).get("variables", {})
        for key in env:
            if any(s in key.lower() for s in ["secret", "password", "token", "key"]):
                return SecurityFinding(
                    rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="Lambda", category=self.metadata().category, base_severity=self.metadata().severity,
                    description=self.metadata().description, root_cause="Hardcoded secrets in ENV.", technical_impact="Developers can read secrets.", business_impact="Credential theft.",
                    recommendation="Use AWS Secrets Manager.", compliance_mapping=self.compliance(),
                    evidence=Evidence(resource_id=node_id, resource_type="Lambda", expected="No secrets", actual=key, reason="Suspicious ENV variable name.", property="environment.variables", raw_data=env)
                )
        return None

class LambdaDLQMissingRule(LambdaBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-LAMBDA-003", version="1.0.0", name="Lambda DLQ Missing", description="Dead Letter Queue is missing.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.RESILIENCE, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["Lambda"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "Lambda"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("dead_letter_config", {}).get("target_arn"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="Lambda", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="No DLQ configured.", technical_impact="Failed async events are dropped.", business_impact="Data loss.",
                recommendation="Configure a DLQ.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="Lambda", expected="DLQ Configured", actual=None, reason="Target ARN is missing.", property="dead_letter_config", raw_data=config)
            )
        return None

class LambdaXRayDisabledRule(LambdaBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-LAMBDA-004", version="1.0.0", name="Lambda X-Ray Disabled", description="Tracing is disabled.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.MONITORING, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["Lambda"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "Lambda"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("tracing_config", {}).get("mode") != "Active":
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="Lambda", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Tracing not active.", technical_impact="Limited observability.", business_impact="Slower MTTR.",
                recommendation="Enable Active tracing.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="Lambda", expected="Active", actual=config.get("tracing_config", {}).get("mode"), reason="Tracing mode is not active.", property="tracing_config", raw_data=config)
            )
        return None

class LambdaReservedConcurrencyRule(LambdaBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-LAMBDA-005", version="1.0.0", name="Lambda Reserved Concurrency Missing", description="No reserved concurrency.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.RESILIENCE, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["Lambda"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.AWS_WELL_ARCHITECTED])
    def supports(self, node_type: str) -> bool: return node_type == "Lambda"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if config.get("concurrency") is None:
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="Lambda", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Concurrency not limited.", technical_impact="Function can consume all account concurrency.", business_impact="Denial of Service to other apps.",
                recommendation="Set a reserved concurrency limit.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="Lambda", expected="Integer", actual=None, reason="Concurrency is None.", property="concurrency", raw_data=config)
            )
        return None

class LambdaCodeSigningDisabledRule(LambdaBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-LAMBDA-006", version="1.0.0", name="Lambda Code Signing Disabled", description="Code signing is not enforced.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.COMPUTE, capability=RuleCapability.DETECTIVE, severity=Severity.MEDIUM, resource_types=["Lambda"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.SOC2])
    def supports(self, node_type: str) -> bool: return node_type == "Lambda"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("code_signing_config_arn"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="Lambda", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="Code signing disabled.", technical_impact="Untrusted code could be executed.", business_impact="Supply chain attack vulnerability.",
                recommendation="Enable code signing.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="Lambda", expected="ARN Configured", actual=None, reason="Missing Code Signing ARN.", property="code_signing_config_arn", raw_data=config)
            )
        return None

class LambdaVPCConfigMissingRule(LambdaBaseRule):
    def metadata(self) -> RuleMetadata:
        return RuleMetadata(id="AWS-LAMBDA-007", version="1.0.0", name="Lambda VPC Config Missing", description="Lambda is not in a VPC.", provider=CloudProvider.AWS, domain=SecurityDomain.AWS, category=SecurityCategory.NETWORK, capability=RuleCapability.DETECTIVE, severity=Severity.LOW, resource_types=["Lambda"], supported_clouds=[CloudProvider.AWS], frameworks=[ComplianceFramework.CIS])
    def supports(self, node_type: str) -> bool: return node_type == "Lambda"
    def compliance(self) -> List[ComplianceFramework]: return self.metadata().frameworks
    def evaluate(self, node_id: str, graph: InfrastructureGraph, context: EngineContext) -> Optional[SecurityFinding]:
        config = self.get_config(graph, node_id)
        if not config.get("vpc_config", {}).get("subnet_ids"):
            return SecurityFinding(
                rule_id=self.metadata().id, rule_name=self.metadata().name, resource_id=node_id, resource_type="Lambda", category=self.metadata().category, base_severity=self.metadata().severity,
                description=self.metadata().description, root_cause="No VPC attachment.", technical_impact="Traffic flows over public internet.", business_impact="Network compliance failure.",
                recommendation="Attach Lambda to private subnets in a VPC.", compliance_mapping=self.compliance(),
                evidence=Evidence(resource_id=node_id, resource_type="Lambda", expected="Subnets configured", actual=None, reason="VPC config missing.", property="vpc_config", raw_data=config)
            )
        return None

class LambdaRuleGroup(SecurityRuleGroup):
    def rules(self) -> List[SecurityRule]:
        return [
            LambdaPublicInvokeRule(), LambdaEnvSecretsRule(), LambdaDLQMissingRule(),
            LambdaXRayDisabledRule(), LambdaReservedConcurrencyRule(), LambdaCodeSigningDisabledRule(),
            LambdaVPCConfigMissingRule()
        ]
