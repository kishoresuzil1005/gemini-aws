import os

builders = [
    ("Subnet", "subnet.py"),
    ("RouteTable", "route_table.py"),
    ("InternetGateway", "igw.py"),
    ("NatGateway", "nat_gateway.py"),
    ("SecurityGroup", "security_group.py"),
    ("NetworkInterface", "eni.py"),
    ("ElasticIP", "elastic_ip.py")
]

template = """from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.builders.common import RELATIONSHIP_MAP

class {class_name}GraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type != "{resource_type}":
                continue
            metadata = res.resource_metadata or {}
            for dep in metadata.get("dependencies", []):
                dep_type = dep.get("type", "").upper()
                relationships.append({
                    "from": res.resource_id,
                    "to": dep["id"],
                    "type": RELATIONSHIP_MAP.get(dep_type, "DEPENDS_ON"),
                    "source_type": "{resource_type}",
                    "target_type": dep.get("type", "")
                })
        return relationships
"""

for res_type, filename in builders:
    class_name = res_type
    if res_type == "NetworkInterface":
        class_name = "ENI"
    
    content = template.replace("{class_name}", class_name).replace("{resource_type}", res_type)
    
    path = os.path.join("backend/app/services/graph/builders/network", filename)
    with open(path, "w") as f:
        f.write(content)
