from typing import List, Dict, Any
from app.models import ResourceDB

class ElastiCacheGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            if res.resource_type in ["ElastiCacheCluster", "ElastiCacheRedis", "ElastiCacheMemcached"] and res.resource_metadata:
                metadata = res.resource_metadata
                
                # Note: ElastiCache native discovery provides subnet_group name and security_groups.
                # In the future, this can be expanded if VPC ID is fetched.
                for sg_id in metadata.get("security_groups", []):
                    relationships.append({
                        "from": res.resource_id,
                        "to": sg_id,
                        "type": "USES_SG",
                        "source_type": res.resource_type,
                        "target_type": "SecurityGroup"
                    })

        return relationships
