from typing import Dict
from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider, GenericResourceType

class UnsupportedResourceError(Exception):
    pass

class ResourceMapper:
    """The Universal Taxonomy Rosetta Stone."""
    
    # Generic -> Provider -> Native Name
    MAPPING: Dict[GenericResourceType, Dict[CloudProvider, str]] = {
        GenericResourceType.COMPUTE: {
            CloudProvider.AWS: "EC2",
            CloudProvider.AZURE: "Virtual Machine",
            CloudProvider.GCP: "Compute Engine"
        },
        GenericResourceType.STORAGE: {
            CloudProvider.AWS: "S3",
            CloudProvider.AZURE: "Blob Storage",
            CloudProvider.GCP: "Cloud Storage"
        },
        GenericResourceType.DATABASE: {
            CloudProvider.AWS: "RDS",
            CloudProvider.AZURE: "Azure SQL",
            CloudProvider.GCP: "Cloud SQL"
        },
        GenericResourceType.LOAD_BALANCER: {
            CloudProvider.AWS: "ALB",
            CloudProvider.AZURE: "App Gateway",
            CloudProvider.GCP: "Load Balancer"
        },
        GenericResourceType.FUNCTION: {
            CloudProvider.AWS: "Lambda",
            CloudProvider.AZURE: "Functions",
            CloudProvider.GCP: "Cloud Functions"
        }
    }

    def get_provider_resource_name(self, generic_type: GenericResourceType, provider: CloudProvider) -> str:
        provider_map = self.MAPPING.get(generic_type)
        if not provider_map:
            raise UnsupportedResourceError(f"Resource type {generic_type.value} is not supported.")
            
        native_name = provider_map.get(provider)
        if not native_name:
            raise UnsupportedResourceError(f"Resource type {generic_type.value} is not supported on {provider.value}.")
            
        return native_name
