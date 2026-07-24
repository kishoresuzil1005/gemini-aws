"""
SOC2 Rule Pack.
"""
from app.services.ai.analyzers.engines.policy.policy_models import (
    PolicyPack, PackMetadata, PackVersion, PackStatus, RuleConfiguration
)

PACK = PolicyPack(
    metadata=PackMetadata(
        id="soc2",
        name="SOC2 Trust Services",
        description="SOC2 rules.",
        version=PackVersion(version="1.0.0", min_engine_version="1.0.0"),
        status=PackStatus.ACTIVE
    ),
    configuration=RuleConfiguration(
        enabled_rules=["AWS-IAM-001"]
    )
)
