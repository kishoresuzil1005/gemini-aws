import os

K8S_DIR = "backend/app/providers/kubernetes/services"
os.makedirs(K8S_DIR, exist_ok=True)

services = [
    "deployment", "service", "pod", "node", "namespace", "ingress", 
    "configmap", "secret", "statefulset", "daemonset", "job", 
    "cronjob", "hpa", "networkpolicy"
]

template = """from typing import Dict, Any, List, Optional
from app.providers.common.client_factory import client_factory

class {class_name}Service:
    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name
        # self.client = client_factory.get_kubernetes_client()

    def list(self, namespace: str = "default") -> List[Dict[str, Any]]:
        return []

    def get(self, name: str, namespace: str = "default") -> Optional[Dict[str, Any]]:
        return None

    def create(self, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        return {{}}

    def update(self, name: str, namespace: str = "default", **kwargs) -> Dict[str, Any]:
        return {{}}

    def delete(self, name: str, namespace: str = "default") -> Dict[str, Any]:
        return {{"status": "deleted"}}
"""

for svc in services:
    class_name = "".join([word.capitalize() for word in svc.split("_")])
    
    content = template.format(class_name=class_name)
    filepath = os.path.join(K8S_DIR, f"{svc}_service.py")
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Created {filepath}")
