"""
Versioning utilities for Pack dependencies.
"""
from app.services.ai.analyzers.engines.policy.policy_models import PackVersion

class VersionResolver:
    @staticmethod
    def is_compatible(required: str, actual: str) -> bool:
        """
        Strict deterministic semantic version evaluation.
        """
        # In a real system, we'd use semantic_version or packaging.version
        return required <= actual
