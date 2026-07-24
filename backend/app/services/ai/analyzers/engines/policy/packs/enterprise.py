"""
Enterprise Environment Profile Pack.
"""
from app.services.ai.analyzers.engines.policy.policy_models import (
    PolicyPack, PackMetadata, PackVersion, PackStatus, RuleConfiguration, RuleOverride, PackDependency
)
from app.services.ai.analyzers.engines.security.security_models import Severity

# Enterprise enables everything and makes severities critical
PACK = PolicyPack(
    metadata=PackMetadata(
        id="enterprise",
        name="Enterprise Baseline",
        description="Strict compliance.",
        version=PackVersion(version="2.0.0", min_engine_version="1.0.0"),
        status=PackStatus.ACTIVE,
        dependencies=[PackDependency(pack_id="aws_cis", min_version="1.0.0")]
    ),
    configuration=RuleConfiguration(
        enabled_rules=["AWS-KMS-001", "AWS-ORG-001", "AWS-SSO-001"]
    ),
    overrides=[
        RuleOverride(rule_id="AWS-S3-001", severity_override=Severity.CRITICAL)
    ]
)
