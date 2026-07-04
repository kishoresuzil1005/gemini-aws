import logging
from sqlalchemy.orm import Session
from app.models import ResourceDB
from typing import List, Dict, Any

from app.services.graph.builders.compute.ec2 import EC2GraphBuilder

logger = logging.getLogger(__name__)

class AWSRelationshipBuilder:
    """
    Phase 4 Relationship Builder.
    Now acts as an orchestrator that passes the database inventory
    to modular category builders. ZERO Boto3 calls.
    """
    def __init__(self, db: Session):
        self.db = db

    def build(self) -> List[Dict[str, Any]]:
        # Read Inventory once
        resources = self.db.query(ResourceDB).all()
        relationships = []
        
        try:
            # 1. Compute
            relationships.extend(EC2GraphBuilder.build(resources))
            
            # 2. Add other category builders here as they are developed
            # relationships.extend(VPCGraphBuilder.build(resources))
            # relationships.extend(LambdaGraphBuilder.build(resources))
            # relationships.extend(S3GraphBuilder.build(resources))
            
            # 3. Fallback: Parse generic dependencies list embedded in metadata by AWSDiscoveryScanner
            for res in resources:
                if res.metadata and "dependencies" in res.metadata:
                    for dep in res.metadata["dependencies"]:
                        if isinstance(dep, dict) and "type" in dep and "id" in dep:
                            relationships.append({
                                "from": res.resource_id,
                                "to": dep["id"],
                                "type": f"USES_{dep['type'].upper()}",
                                "source_type": res.resource_type,
                                "target_type": dep["type"]
                            })

        except Exception as e:
            logger.error(f"Error building graph from inventory: {e}")
            
        return relationships
