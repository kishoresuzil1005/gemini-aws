from typing import Dict, Any

class FeatureFlagManager:
    """
    Toggles platform features globally or per-tenant for A/B testing and phased rollouts.
    """
    def __init__(self):
        self._flags = {
            "enable_kubernetes_agent": True,
            "enable_advanced_mission_analytics": False
        }
        self._tenant_overrides = {}

    def is_enabled(self, flag_name: str, tenant_id: str = None) -> bool:
        if tenant_id and tenant_id in self._tenant_overrides:
            if flag_name in self._tenant_overrides[tenant_id]:
                return self._tenant_overrides[tenant_id][flag_name]
        return self._flags.get(flag_name, False)
