from typing import Dict, Any
from app.providers.base_provider import BaseCloudProvider
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericResourceType
from app.providers.kubernetes.auth import KubernetesAuth
from app.providers.kubernetes.response_normalizer import KubernetesResponseNormalizer
from app.providers.kubernetes.translator import KubernetesTranslator

# Services
from app.providers.kubernetes.services.deployment_service import DeploymentService
from app.providers.kubernetes.services.pod_service import PodService

class KubernetesProvider(BaseCloudProvider):
    def __init__(self):
        self.auth = KubernetesAuth()
        self.deployment = DeploymentService(self.auth)
        self.pod = PodService(self.auth)

    @property
    def name(self) -> CloudProvider:
        return CloudProvider.KUBERNETES

    def execute_action(self, action: str, resource_id: str, **kwargs) -> Dict[str, Any]:
        """
        The generic entrypoint from the MultiCloud engine.
        """
        try:
            res_type = kwargs.pop("generic_resource_type", None)
            
            from app.services.ai.assistant.multicloud.multicloud_models import TranslatedActionPayload
            payload = TranslatedActionPayload(provider=self.name, api_call=action, payload={"resource_id": resource_id, **kwargs})
            method_name, final_kwargs = KubernetesTranslator().translate(payload)
            
            # Simple routing based on generic resource type or more specific k8s kinds if needed
            # For this MVP phase, we map COMPUTE to Deployment, but ideally we'd look at the k8s resource type
            # parsed from resource_id.
            
            from app.providers.kubernetes.resource_parser import ResourceParser
            parsed = ResourceParser.parse(resource_id)
            k8s_type = parsed.get("resource_type") or "deployments"
            
            if k8s_type == "deployments":
                raw_response = self.deployment.execute(method_name, **final_kwargs)
            elif k8s_type == "pods":
                raw_response = self.pod.execute(method_name, **final_kwargs)
            else:
                raw_response = {"status": "success", "message": f"Kubernetes Executed {action} on {resource_id} (Unmapped Service)"}
                
            return KubernetesResponseNormalizer.normalize(raw_response).model_dump()
            
        except Exception as e:
            return KubernetesResponseNormalizer.normalize_error(str(e)).model_dump()
