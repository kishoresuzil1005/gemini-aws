from app.providers.kubernetes.auth import KubernetesAuth
from app.providers.common.base_service import BaseService

class DeploymentService(BaseService):
    def __init__(self, auth: KubernetesAuth):
        self.auth = auth
        self.api = auth.apps_v1

    def execute(self, method_name: str, **kwargs):
        # We use BaseService's _execute_with_retry for resiliency
        def _call_api():
            # Example mapping: STOP -> Scale to 0
            if method_name == "STOP":
                resource_id = kwargs.get("resource_id", "")
                from app.providers.kubernetes.resource_parser import ResourceParser
                parsed = ResourceParser.parse(resource_id)
                name = parsed.get("resource_name")
                ns = parsed.get("namespace", "default")
                
                body = {"spec": {"replicas": 0}}
                return self.api.patch_namespaced_deployment_scale(name=name, namespace=ns, body=body)
                
            # Default dynamic calling
            if hasattr(self.api, method_name):
                method = getattr(self.api, method_name)
                return method(**kwargs)
            raise ValueError(f"Unknown deployment method: {method_name}")
            
        return self._execute_with_retry(_call_api)
