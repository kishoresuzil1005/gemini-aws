"""
Environment Profiles for the Policy Engine.
"""
from typing import Dict, List
from app.services.ai.analyzers.engines.policy.policy_models import EnvironmentProfile, EnvironmentType, RuleOverride

class EnvironmentProfileRegistry:
    """
    Registry for predefined environment profiles mapping environments to packs.
    """
    def __init__(self):
        self._profiles: Dict[EnvironmentType, EnvironmentProfile] = {}
        self._initialize_defaults()

    def _initialize_defaults(self):
        self.register(EnvironmentProfile(
            environment=EnvironmentType.STARTUP,
            active_packs=["aws_cis", "startup"]
        ))
        self.register(EnvironmentProfile(
            environment=EnvironmentType.ENTERPRISE,
            active_packs=["aws_cis", "nist", "soc2", "enterprise", "production"]
        ))
        self.register(EnvironmentProfile(
            environment=EnvironmentType.DEVELOPMENT,
            active_packs=["aws_cis", "development"]
        ))
        self.register(EnvironmentProfile(
            environment=EnvironmentType.PRODUCTION,
            active_packs=["aws_cis", "production"]
        ))
        
    def register(self, profile: EnvironmentProfile):
        self._profiles[profile.environment] = profile
        
    def get_profile(self, env: EnvironmentType) -> EnvironmentProfile:
        return self._profiles.get(env, EnvironmentProfile(environment=env))
