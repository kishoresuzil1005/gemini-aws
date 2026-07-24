"""
Feature Flags for the Policy Engine.
"""
from typing import Dict, List
from app.services.ai.analyzers.engines.policy.policy_models import FeatureFlag, RuleStatus

class FeatureFlagManager:
    """
    Manages resolution of conflicting feature flags.
    """
    @staticmethod
    def resolve_flags(flags: List[FeatureFlag]) -> Dict[str, RuleStatus]:
        resolved: Dict[str, RuleStatus] = {}
        for flag in flags:
            # Later flags overwrite earlier ones in resolution order
            resolved[flag.rule_id] = flag.status
        return resolved
