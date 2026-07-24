"""
O(N) Engine for managing and merging Policy Packs.
"""
from typing import List, Dict, Set
from app.services.ai.analyzers.engines.policy.policy_models import (
    EnvironmentType, ExecutionProfile, PolicyPack, RuleOverride, RuleStatus
)
from app.services.ai.analyzers.engines.policy.pack_registry import PackRegistry
from app.services.ai.analyzers.engines.policy.environment_profiles import EnvironmentProfileRegistry
from app.services.ai.analyzers.engines.policy.policy_validator import PolicyValidator
from app.services.ai.analyzers.engines.policy.feature_flags import FeatureFlagManager

class PolicyEngine:
    """
    Stateless, thread-safe aggregator for Rule Pack execution.
    """
    def __init__(self, registry: PackRegistry = None, profile_registry: EnvironmentProfileRegistry = None):
        self.registry = registry or PackRegistry()
        self.profile_registry = profile_registry or EnvironmentProfileRegistry()
        self.validator = PolicyValidator()
        self.flag_manager = FeatureFlagManager()

    def _merge_packs(self, packs: List[PolicyPack]) -> ExecutionProfile:
        active_rules: Set[str] = set()
        overrides: Dict[str, RuleOverride] = {}
        all_flags = []
        
        for pack in packs:
            # Enable rules
            for rule_id in pack.configuration.enabled_rules:
                active_rules.add(rule_id)
                
            # Disable rules
            for rule_id in pack.configuration.disabled_rules:
                active_rules.discard(rule_id)
                
            # Apply overrides (Last-writer wins for conflicts)
            for override in pack.overrides:
                if override.rule_id in overrides:
                    # Merge existing override
                    existing = overrides[override.rule_id]
                    merged_tags_add = list(set(existing.tags_add + override.tags_add))
                    merged_tags_remove = list(set(existing.tags_remove + override.tags_remove))
                    
                    overrides[override.rule_id] = RuleOverride(
                        rule_id=override.rule_id,
                        severity_override=override.severity_override or existing.severity_override,
                        category_override=override.category_override or existing.category_override,
                        priority_override=override.priority_override or existing.priority_override,
                        tags_add=merged_tags_add,
                        tags_remove=merged_tags_remove
                    )
                else:
                    overrides[override.rule_id] = override
                    
            # Collect flags
            all_flags.extend(pack.feature_flags)
            
        # Resolve feature flags
        resolved_statuses = self.flag_manager.resolve_flags(all_flags)
        
        # We don't have environment here yet since it's an internal function, so dummy it for now
        # Actually this method just resolves the packs.
        
        return ExecutionProfile(
            environment=EnvironmentType.DEVELOPMENT, # Overwritten below
            active_rules=active_rules,
            rule_overrides=overrides,
            rule_statuses=resolved_statuses
        )

    def resolve_environment(self, environment: EnvironmentType) -> ExecutionProfile:
        """
        Resolves the exact execution profile based on the environment.
        """
        profile = self.profile_registry.get_profile(environment)
        
        packs_to_merge = []
        for pack_id in profile.active_packs:
            pack = self.registry.get_pack(pack_id)
            if pack:
                packs_to_merge.append(pack)
                
        # Validate packs
        if not self.validator.validate_packs(packs_to_merge):
            raise ValueError(f"Invalid pack combination for environment {environment}")
            
        execution_profile = self._merge_packs(packs_to_merge)
        
        # Apply global environment overrides
        # Re-using the Pydantic dict reconstruction pattern for immutable updates
        merged_overrides = dict(execution_profile.rule_overrides)
        for override in profile.global_overrides:
             merged_overrides[override.rule_id] = override
             
        return ExecutionProfile(
            environment=environment,
            active_rules=execution_profile.active_rules,
            rule_overrides=merged_overrides,
            rule_statuses=execution_profile.rule_statuses
        )
