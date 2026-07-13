import os

AZURE_DIR = "backend/app/providers/azure/services"
os.makedirs(AZURE_DIR, exist_ok=True)

services = [
    "network", "storage", "sql", "monitor", "aks", "keyvault", "advisor", "policy"
]

template = """from typing import Dict, Any, List, Optional
from app.providers.common.client_factory import client_factory

class {class_name}Service:
    def __init__(self, subscription_id: str):
        self.subscription_id = subscription_id
        # Client would typically be obtained via client_factory.get_azure_client(..., credential)
        # self.client = client_factory.get_azure_client("{service_type}")

    def list(self) -> List[Dict[str, Any]]:
        return []

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        return None

    def create(self, **kwargs) -> Dict[str, Any]:
        return {{}}

    def update(self, resource_id: str, **kwargs) -> Dict[str, Any]:
        return {{}}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        return {{"status": "deleted"}}
"""

for svc in services:
    class_name = "".join([word.capitalize() for word in svc.split("_")])
    
    content = template.format(class_name=class_name, service_type=svc)
    filepath = os.path.join(AZURE_DIR, f"{svc}_service.py")
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Created {filepath}")
