"""
Startup Environment Profile Pack.
"""
from app.services.ai.analyzers.engines.policy.policy_models import (
    PolicyPack, PackMetadata, PackVersion, PackStatus, RuleConfiguration, RuleOverride
)
from app.services.ai.analyzers.engines.security.security_models import Severity

# Startup disables expensive rules or lowers severity for agility
PACK = PolicyPack(
    metadata=PackMetadata(
        id="startup",
        name="Startup Baseline",
        description="Agile baseline with lower enforcement.",
        version=PackVersion(version="1.0.0", min_engine_version="1.0.0"),
        status=PackStatus.ACTIVE
    ),
    configuration=RuleConfiguration(
        disabled_rules=["AWS-CT-001"] # Logging might be too expensive initially
    ),
    overrides=[
        RuleOverride(rule_id="AWS-S3-001", severity_override=Severity.MEDIUM)
    ]
)
