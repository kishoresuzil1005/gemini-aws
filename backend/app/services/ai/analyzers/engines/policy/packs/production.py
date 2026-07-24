"""
Production Environment Profile Pack.
"""
from app.services.ai.analyzers.engines.policy.policy_models import (
    PolicyPack, PackMetadata, PackVersion, PackStatus, RuleConfiguration, FeatureFlag, RuleStatus
)

# Production strictly enables rules in DETECT or PREVENT mode
PACK = PolicyPack(
    metadata=PackMetadata(
        id="production",
        name="Production Enforcer",
        description="Production overrides.",
        version=PackVersion(version="1.0.0", min_engine_version="1.0.0"),
        status=PackStatus.ACTIVE
    ),
    configuration=RuleConfiguration(
        enabled_rules=["AWS-RDS-001"]
    ),
    feature_flags=[
        FeatureFlag(rule_id="AWS-RDS-001", status=RuleStatus.ENABLED)
    ]
)
