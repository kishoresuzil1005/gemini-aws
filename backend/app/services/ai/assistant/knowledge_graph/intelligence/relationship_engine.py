from typing import List
from app.services.ai.assistant.knowledge_graph.models.knowledge_models import CloudNode, CloudEdge

class RelationshipEngine:
    """Infers edges dynamically based on node properties and structural logic."""
    
    def infer_relationships(self, nodes: List[CloudNode]) -> List[CloudEdge]:
        """
        Example: EC2 node has a property 'subnet_id: subnet-123'. 
        If a Subnet node exists with ID 'subnet-123', create BELONGS_TO edge.
        """
        edges = []
        
        # Build lookup table for fast inference
        lookup = {n.node_id: n for n in nodes}
        
        for node in nodes:
            if node.provider == "AWS" and node.resource_type == "instance":
                subnet_id = node.properties.get("subnet_id")
                if subnet_id:
                    # Construct ARN or identifier for subnet
                    subnet_urn = f"arn:aws:ec2:us-east-1:123456789012:subnet/{subnet_id}"
                    if subnet_urn in lookup:
                        edges.append(CloudEdge(
                            source_id=node.node_id,
                            target_id=subnet_urn,
                            relationship_type="BELONGS_TO"
                        ))
                        
            elif node.provider == "KUBERNETES" and node.resource_type == "pods":
                # E.g., pod -> namespace
                if node.properties.get("namespace"):
                    pass # build edge
                    
        return edge