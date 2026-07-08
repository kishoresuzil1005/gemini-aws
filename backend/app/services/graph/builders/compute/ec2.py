from typing import List, Dict, Any
from app.models import ResourceDB
from app.services.graph.helpers.graph_metadata_helper import GraphMetadataHelper
from app.services.graph.helpers.graph_relationship import GraphRelationship
from app.services.graph.helpers.relationship_types import RelationshipType
from app.services.graph.helpers.graph_validation import GraphValidation

class EC2GraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        raw_edges = []
        resource_lookup = {r.resource_id: r.resource_type for r in resources}
        
        for res in resources:
            if res.resource_type != "EC2":
                continue
                
            config = GraphMetadataHelper.get_compute(res)
            security = GraphMetadataHelper.get_security(res)
            
            # Pre-build validation
            if not GraphValidation.validate_pre_build(config, ["vpc_id"]):
                # Usually we might skip or just log, but let's proceed with what we have
                pass
            
            # EC2 -> VPC
            vpc_id = config.get("vpc_id")
            if vpc_id:
                edge = GraphRelationship.create(
                    source=res.resource_id,
                    target=vpc_id,
                    relationship=RelationshipType.IN_VPC,
                    source_type="EC2",
                    target_type="VPC"
                )
                if edge: raw_edges.append(edge)
                
            # EC2 -> Subnet
            subnet_id = config.get("subnet_id")
            if subnet_id:
                edge = GraphRelationship.create(
                    source=res.resource_id,
                    target=subnet_id,
                    relationship=RelationshipType.IN_SUBNET,
                    source_type="EC2",
                    target_type="Subnet"
                )
                if edge: raw_edges.append(edge)
                
            # EC2 -> EBS Volumes
            for ebs_id in config.get("ebs_volumes", []):
                edge = GraphRelationship.create(
                    source=res.resource_id,
                    target=ebs_id,
                    relationship=RelationshipType.ATTACHED_TO,
                    source_type="EC2",
                    target_type="EBS"
                )
                if edge: raw_edges.append(edge)
                    
            # EC2 -> Security Groups
            for sg_id in security.get("security_groups", []):
                edge = GraphRelationship.create(
                    source=res.resource_id,
                    target=sg_id,
                    relationship=RelationshipType.USES_SG,
                    source_type="EC2",
                    target_type="SecurityGroup"
                )
                if edge: raw_edges.append(edge)
                    
            # EC2 -> IAM Role / Instance Profile
            iam_profile = security.get("iam_instance_profile")
            if iam_profile:
                edge = GraphRelationship.create(
                    source=res.resource_id,
                    target=iam_profile,
                    relationship=RelationshipType.USES_ROLE,
                    source_type="EC2",
                    target_type="IAM"
                )
                if edge: raw_edges.append(edge)
                
        # Post-build validation: filter out invalid targets and duplicates
        return GraphValidation.validate_post_build(raw_edges, resource_lookup)
