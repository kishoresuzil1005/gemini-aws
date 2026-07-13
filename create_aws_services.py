import os

AWS_DIR = "backend/app/providers/aws"
os.makedirs(AWS_DIR, exist_ok=True)

# Generate basic skeleton for all requested AWS services
services = [
    "internet_gateway", "nat_gateway", "route_table", "subnet", "network_interface", "elastic_ip",
    "load_balancer", "target_group", "listener", "autoscaling", "security_group", 
    "s3", "ebs", "cloudtrail", "config", "backup", "ssm"
]

template = """from typing import Dict, Any, List, Optional
from app.providers.common.client_factory import client_factory

class {class_name}Service:
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self.client = client_factory.get_aws_client("{boto_service}", region_name=region)

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

boto_mapping = {
    "s3": "s3",
    "load_balancer": "elbv2",
    "target_group": "elbv2",
    "listener": "elbv2",
    "autoscaling": "autoscaling",
    "cloudtrail": "cloudtrail",
    "config": "config",
    "backup": "backup",
    "ssm": "ssm"
}

for svc in services:
    class_name = "".join([word.capitalize() for word in svc.split("_")])
    boto_svc = boto_mapping.get(svc, "ec2") # Default to ec2 for networking
    
    content = template.format(class_name=class_name, boto_service=boto_svc)
    filepath = os.path.join(AWS_DIR, f"{svc}_service.py")
    with open(filepath, "w") as f:
        f.write(content)
    print(f"Created {filepath}")
