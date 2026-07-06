import logging
from sqlalchemy.orm import Session
from app.models import ResourceDB
from typing import List, Dict, Any

from app.services.graph.builders.compute.ec2 import EC2GraphBuilder
from app.services.graph.builders.compute.lambda_builder import LambdaGraphBuilder
from app.services.graph.builders.database.rds import RDSGraphBuilder
from app.services.graph.builders.storage.s3 import S3GraphBuilder
from app.services.graph.builders.network.vpc import VPCGraphBuilder

logger = logging.getLogger(__name__)

RELATIONSHIP_MAP = {
    "VPC": "IN_VPC",
    "SUBNET": "IN_SUBNET",
    "SECURITYGROUP": "USES_SG",
    "SECURITY_GROUP": "USES_SG",
    "SG": "USES_SG",
    "EBS": "ATTACHED_TO",
    "VOLUME": "ATTACHED_TO",
    "IAM": "USES_ROLE",
    "IAM_ROLE": "USES_ROLE",
    "IAMUSER": "USES_ROLE",
    "TARGETGROUP": "TARGETS",
    "LOADBALANCER": "ATTACHED_TO",
    "ALB": "ATTACHED_TO",
    "LAMBDA": "INVOKES",
    "S3": "USES_BUCKET",
    "RDS": "CONNECTS_TO"
}

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
            relationships.extend(EC2GraphBuilder.build(resources))
            relationships.extend(LambdaGraphBuilder.build(resources))
            relationships.extend(RDSGraphBuilder.build(resources))
            relationships.extend(S3GraphBuilder.build(resources))
            
            # Networking
            relationships.extend(VPCGraphBuilder.build(resources))
        except Exception as e:
            logger.error(f"Error building graph from inventory: {e}")
            
        return relationships
