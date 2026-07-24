"""
Development Environment Profile Pack.
"""
from app.services.ai.analyzers.engines.policy.policy_models import (
    PolicyPack, PackMetadata, PackVersion, PackStatus, RuleConfiguration, FeatureFlag, RuleStatus
)

# Development downgrades many rules to AUDIT_ONLY
PACK = PolicyPack(
    metadata=PackMetadata(
        id="development",
        name="Development Sandbox",
        description="Relaxed rules for devs.",
        version=PackVersion(version="1.0.0", min_engine_version="1.0.0"),
        status=PackStatus.ACTIVE
    ),
    configuration=RuleConfiguration(),
    feature_flags=[
        FeatureFlag(rule_id="AWS-RDS-001", status=RuleStatus.AUDIT_ONLY),
        FeatureFlag(rule_id="AWS-S3-001", status=RuleStatus.WARNING_ONLY)
    ]
)
