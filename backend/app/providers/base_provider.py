from typing import Dict, Any, Optional
from pydantic import BaseModel
from abc import ABC, abstractmethod

from app.services.ai.assistant.multicloud.multicloud_models import CloudProvider

class BaseCloudProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> CloudProvider:
        pass

    @abstractmethod
    def execute_action(self, action: str, resource_id: str, **kwargs) -> Dict[str, Any]:
        """Executes a cloud action on a resource."""
        pass
