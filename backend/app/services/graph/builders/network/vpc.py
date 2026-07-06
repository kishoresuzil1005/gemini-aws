from typing import List, Dict, Any
from app.models import ResourceDB

class VPCGraphBuilder:
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        relationships = []
        for res in resources:
            metadata = res.resource_metadata or {}
            
            # Subnet -> VPC
            if res.resource_type == "Subnet":
                vpc_id = metadata.get("vpc_id")
                if vpc_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": vpc_id,
                        "type": "IN_VPC",
                        "source_type": "Subnet",
                        "target_type": "VPC"
                    })

            # SecurityGroup -> VPC
            elif res.resource_type == "SecurityGroup":
                vpc_id = metadata.get("vpc_id")
                if vpc_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": vpc_id,
                        "type": "IN_VPC",
                        "source_type": "SecurityGroup",
                        "target_type": "VPC"
                    })

            # RouteTable -> VPC
            elif res.resource_type == "RouteTable":
                vpc_id = metadata.get("vpc_id")
                if vpc_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": vpc_id,
                        "type": "IN_VPC",
                        "source_type": "RouteTable",
                        "target_type": "VPC"
                    })
                
                # RouteTable -> Subnet
                for subnet_id in metadata.get("subnets", []):
                    relationships.append({
                        "from": res.resource_id,
                        "to": subnet_id,
                        "type": "ASSOCIATED_WITH",
                        "source_type": "RouteTable",
                        "target_type": "Subnet"
                    })
                
                # RouteTable -> IGW
                for igw_id in metadata.get("internet_gateways", []):
                    relationships.append({
                        "from": res.resource_id,
                        "to": igw_id,
                        "type": "ROUTES_TO",
                        "source_type": "RouteTable",
                        "target_type": "InternetGateway"
                    })
                    
                # RouteTable -> NAT
                for nat_id in metadata.get("nat_gateways", []):
                    relationships.append({
                        "from": res.resource_id,
                        "to": nat_id,
                        "type": "ROUTES_TO",
                        "source_type": "RouteTable",
                        "target_type": "NatGateway"
                    })

            # InternetGateway -> VPC
            elif res.resource_type == "InternetGateway":
                # IGWs in our discovery might not have vpc_id in metadata natively
                # But they are attached to VPCs. We'll handle if it's there.
                vpc_id = metadata.get("vpc_id")
                if vpc_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": vpc_id,
                        "type": "ATTACHED_TO",
                        "source_type": "InternetGateway",
                        "target_type": "VPC"
                    })

            # NatGateway -> VPC & Subnet
            elif res.resource_type == "NatGateway":
                vpc_id = metadata.get("vpc_id")
                if vpc_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": vpc_id,
                        "type": "IN_VPC",
                        "source_type": "NatGateway",
                        "target_type": "VPC"
                    })
                subnet_id = metadata.get("subnet_id")
                if subnet_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": subnet_id,
                        "type": "IN_SUBNET",
                        "source_type": "NatGateway",
                        "target_type": "Subnet"
                    })

            # NetworkInterface -> VPC & Subnet & SecurityGroup
            elif res.resource_type == "NetworkInterface":
                vpc_id = metadata.get("vpc_id")
                if vpc_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": vpc_id,
                        "type": "IN_VPC",
                        "source_type": "NetworkInterface",
                        "target_type": "VPC"
                    })
                subnet_id = metadata.get("subnet_id")
                if subnet_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": subnet_id,
                        "type": "IN_SUBNET",
                        "source_type": "NetworkInterface",
                        "target_type": "Subnet"
                    })
                for sg in metadata.get("security_groups", []):
                    sg_id = sg.get("GroupId") if isinstance(sg, dict) else sg
                    if sg_id:
                        relationships.append({
                            "from": res.resource_id,
                            "to": sg_id,
                            "type": "USES_SG",
                            "source_type": "NetworkInterface",
                            "target_type": "SecurityGroup"
                        })

            # ElasticIP -> NetworkInterface
            elif res.resource_type == "ElasticIP":
                eni_id = metadata.get("network_interface_id")
                if eni_id:
                    relationships.append({
                        "from": res.resource_id,
                        "to": eni_id,
                        "type": "ATTACHED_TO",
                        "source_type": "ElasticIP",
                        "target_type": "NetworkInterface"
                    })

        return relationships
