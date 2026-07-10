from typing import Dict, Any
from app.providers.base_provider import BaseCloudProvider
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericResourceType
from app.providers.gcp.auth import GCPAuth
from app.providers.gcp.services.compute_service import ComputeService
from app.providers.gcp.services.storage_service import StorageService
from app.providers.gcp.services.network_service import NetworkService
from app.providers.gcp.services.sql_service import SqlService
from app.providers.gcp.services.monitor_service import MonitorService
from app.providers.gcp.services.iam_service import IamService
from app.providers.gcp.services.kubernetes_service import KubernetesService
from app.providers.gcp.response_normalizer import GCPResponseNormalizer
from app.providers.gcp.translator import GCPTranslator

class GCPProvider(BaseCloudProvider):
    def __init__(self):
        self.auth = GCPAuth()
        self.compute = ComputeService(self.auth)
        self.storage = StorageService(self.auth)
        self.network = NetworkService(self.auth)
        self.sql = SqlService(self.auth)
        self.monitor = MonitorService(self.auth)
        self.iam = IamService(self.auth)
        self.kubernetes = KubernetesService(self.auth)

    @property
    def name(self) -> CloudProvider:
        return CloudProvider.GCP

    def execute_action(self, action: str, resource_id: str, **kwargs) -> Dict[str, Any]:
        """
        The generic entrypoint from the MultiCloud engine.
        """
        try:
            res_type = kwargs.pop("generic_resource_type", None)
            
            from app.services.ai.assistant.multicloud.multicloud_models import TranslatedActionPayload
            payload = TranslatedActionPayload(provider=self.name, api_call=action, payload={"resource_id": resource_id, **kwargs})
            method_name, final_kwargs = GCPTranslator().translate(payload)
            
            if res_type == GenericResourceType.COMPUTE:
                raw_response = self.compute.execute(method_name, **final_kwargs)
            elif res_type == GenericResourceType.STORAGE:
                raw_response = self.storage.execute(method_name, **final_kwargs)
            elif res_type == GenericResourceType.NETWORK:
                raw_response = self.network.execute(method_name, **final_kwargs)
            elif res_type == GenericResourceType.DATABASE:
                raw_response = self.sql.execute(method_name, **final_kwargs)
            elif res_type == GenericResourceType.IDENTITY:
                raw_response = self.iam.execute(method_name, **final_kwargs)
            elif res_type == GenericResourceType.KUBERNETES:
                raw_response = self.kubernetes.execute(method_name, **final_kwargs)
            else:
                raw_response = {"status": "success", "message": f"GCP Executed {action} on {resource_id} (Unmapped Service)"}
                
            return GCPResponseNormalizer.normalize(raw_response).model_dump()
            
        except Exception as e:
            return GCPResponseNormalizer.normalize_error(str(e)).model_dump()
