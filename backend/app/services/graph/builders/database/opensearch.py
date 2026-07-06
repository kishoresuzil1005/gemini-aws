from typing import List, Dict, Any
from app.models import ResourceDB

class OpenSearchGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type == "OpenSearchDomain" and res.resource_metadata:
                metadata = res.resource_metadata
                
                # OpenSearch -> VPC
                vpc_id = metadata.get("vpc_id")
                if vpc_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": vpc_id,
                        "type": "IN_VPC",
                        "source_type": "OpenSearch",
                        "target_type": "VPC"
                    })
                
                # OpenSearch -> Subnet
                for subnet_id in metadata.get("subnet_ids", []):
                    relationships.append({
                        "from": res.resource_id,
                        "to": subnet_id,
                        "type": "IN_SUBNET",
                        "source_type": "OpenSearch",
                        "target_type": "Subnet"
                    })
                    
                # OpenSearch -> SecurityGroup
                for sg_id in metadata.get("security_groups", []):
                    relationships.append({
                        "from": res.resource_id,
                        "to": sg_id,
                        "type": "USES_SG",
                        "source_type": "OpenSearch",
                        "target_type": "SecurityGroup"
                    })

        return relationships
