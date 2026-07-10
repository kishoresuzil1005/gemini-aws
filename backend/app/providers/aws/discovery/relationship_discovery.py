from typing import Dict, Any, List, Tuple

class RelationshipDiscovery:
    """
    Analyzes raw AWS resources and automatically infers architectural 
    dependencies and relationships without manual tagging.
    """
    def build_graph(self, raw_inventory: Dict[str, List[Any]]) -> Tuple[List[Dict], List[Dict]]:
        print("[RelationshipDiscovery] Building dependency graph from raw inventory...")
        nodes = []
        edges = []

        # Parse EC2 to Subnet to VPC relationships
        for instance in raw_inventory.get("ec2_instances", []):
            instance_id = instance.get("InstanceId")
            subnet_id = instance.get("SubnetId")
            vpc_id = instance.get("VpcId")
            
            nodes.append({"id": instance_id, "type": "AWS::EC2::Instance", "properties": instance})
            
            if subnet_id:
                edges.append({"source": instance_id, "target": subnet_id, "relation": "DEPLOYED_IN"})
            if vpc_id:
                edges.append({"source": instance_id, "target": vpc_id, "relation": "BELONGS_TO"})
                
            for sg in instance.get("SecurityGroups", []):
                edges.append({"source": instance_id, "target": sg.get("GroupId"), "relation": "USES_SECURITY_GROUP"})

        # (Placeholder for VPC, RDS, S3 parsing...)
        
        return nodes, edges
