"""
HIPAA Rule Pack.
"""
from app.services.ai.analyzers.engines.policy.policy_models import (
    PolicyPack, PackMetadata, PackVersion, PackStatus, RuleConfiguration
)

PACK = PolicyPack(
    metadata=PackMetadata(
        id="hipaa",
        name="HIPAA Security Rule",
        description="HIPAA rules.",
        version=PackVersion(version="1.0.0", min_engine_version="1.0.0"),
        status=PackStatus.ACTIVE
    ),
    configuration=RuleConfiguration(
        enabled_rules=["AWS-IAM-001"]
    )
)
