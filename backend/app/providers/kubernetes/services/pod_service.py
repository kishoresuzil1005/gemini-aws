from app.providers.kubernetes.auth import KubernetesAuth
from app.providers.common.base_service import BaseService

class PodService(BaseService):
    def __init__(self, auth: KubernetesAuth):
        self.auth = auth
        self.api = auth.core_v1

    def execute(self, method_name: str, **kwargs):
        def _call_api():
            if hasattr(self.api, method_name):
                method = getattr(self.api, method_name)
                return method(**kwargs)
            raise ValueError(f"Unknown pod method: {method_name}")
            
        return self._execute_with_retry(_call_api)
