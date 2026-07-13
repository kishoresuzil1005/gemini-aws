from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from abc import ABC, abstractmethod

from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider

class BaseCloudProvider(ABC):
    """
    Standardized Cloud Provider Interface.
    Every cloud provider (AWS, Azure, GCP, Kubernetes) must implement these methods.
    """

    @property
    @abstractmethod
    def name(self) -> CloudProvider:
        pass

    @abstractmethod
    def discover(self, region: Optional[str] = None) -> List[Dict[str, Any]]:
        """Discovers resources across the provider."""
        pass

    @abstractmethod
    def get_resource(self, resource_type: str, resource_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Fetches a single resource by ID."""
        pass

    @abstractmethod
    def list_resources(self, resource_type: str, **kwargs) -> List[Dict[str, Any]]:
        """Lists all resources of a specific type."""
        pass

    @abstractmethod
    def execute_action(self, action: str, resource_id: str, **kwargs) -> Dict[str, Any]:
        """Executes a cloud action on a resource."""
        pass

    @abstractmethod
    def delete(self, resource_type: str, resource_id: str, **kwargs) -> Dict[str, Any]:
        """Deletes a resource."""
        pass

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """Returns the health status of the provider."""
        pass

    @abstractmethod
    def metrics(self) -> Dict[str, Any]:
        """Returns provider-specific metrics (API calls, errors, latency)."""
        pass

    @abstractmethod
    def capabilities(self) -> List[str]:
        """Returns statically defined capabilities of this provider."""
        pass

    @abstractmethod
    def discover_capabilities(self) -> List[str]:
        """Dynamically discovers the supported capabilities/services of this provider."""
        pass
