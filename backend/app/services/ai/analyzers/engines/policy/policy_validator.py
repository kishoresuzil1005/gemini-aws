"""
Validator for Policy Packs and Execution Profiles.
"""
from typing import List, Dict
from app.services.ai.analyzers.engines.policy.policy_models import PolicyPack

class PolicyValidator:
    """
    Validates Policy Packs for conflicts and circular dependencies.
    """
    @staticmethod
    def validate_packs(packs: List[PolicyPack]) -> bool:
        """
        Validates a collection of packs before merging.
        """
        seen_ids = set()
        for pack in packs:
            if pack.metadata.id in seen_ids:
                return False # Duplicate pack ID
            seen_ids.add(pack.metadata.id)
            
        # Check dependencies
        for pack in packs:
            for dep in pack.metadata.dependencies:
                if dep.pack_id not in seen_ids:
                    return False # Missing dependency
                    
        return True
