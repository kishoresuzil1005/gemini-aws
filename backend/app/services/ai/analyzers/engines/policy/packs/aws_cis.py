"""
AWS CIS Rule Pack.
"""
from app.services.ai.analyzers.engines.policy.policy_models import (
    PolicyPack, PackMetadata, PackVersion, PackStatus, RuleConfiguration
)

PACK = PolicyPack(
    metadata=PackMetadata(
        id="aws_cis",
        name="AWS CIS Foundations",
        description="CIS benchmark rules.",
        version=PackVersion(version="1.4.0", min_engine_version="1.0.0"),
        status=PackStatus.ACTIVE
    ),
    configuration=RuleConfiguration(
        enabled_rules=["AWS-IAM-001", "AWS-S3-001", "AWS-CT-001"]
    )
)
