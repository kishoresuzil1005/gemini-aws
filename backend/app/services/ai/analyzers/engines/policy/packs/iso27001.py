"""
ISO27001 Rule Pack.
"""
from app.services.ai.analyzers.engines.policy.policy_models import (
    PolicyPack, PackMetadata, PackVersion, PackStatus, RuleConfiguration
)

PACK = PolicyPack(
    metadata=PackMetadata(
        id="iso27001",
        name="ISO27001",
        description="ISO rules.",
        version=PackVersion(version="1.0.0", min_engine_version="1.0.0"),
        status=PackStatus.ACTIVE
    ),
    configuration=RuleConfiguration(
        enabled_rules=["AWS-IAM-001"]
    )
)
