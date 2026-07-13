from collections import defaultdict

from app.services.diagram.topology_builder import TopologyBuilder


class VPCAZBuilder:
    """
    Groups topology into:

    VPC
      ├── Availability Zones
      ├── Public Subnets
      └── Private Subnets
    """

    def __init__(self):
        self.topology = TopologyBuilder()

    def build(self):

        topology = self.topology.build()

        vpcs = []

        for tree in topology["topology"]:

            self._walk(tree, None, None, None, vpcs)

        return {
            "vpcs": vpcs
        }

    def _walk(
        self,
        node,
        current_vpc,
        current_az,
        current_subnet,
        vpcs
    ):

        node_type = node["type"]
        metadata = node.get("metadata", {})

        #
        # VPC
        #
        if node_type == "VPC":
            current_vpc = {
                "id": node["id"],
                "name": node.get("name"),
                "cidr": metadata.get("cidr_block"),
                "region": metadata.get("region"),
                "availability_zones": []
            }
            vpcs.append(current_vpc)

        #
        # Subnet
        #
        elif node_type == "Subnet":
            az = (
                metadata.get("availability_zone")
                or metadata.get("AvailabilityZone")
                or "unknown"
            )

            current_az = None

            if current_vpc:
                for zone in current_vpc["availability_zones"]:
                    if zone["name"] == az:
                        current_az = zone
                        break

                if current_az is None:
                    current_az = {
                        "name": az,
                        "public_subnets": [],
                        "private_subnets": []
                    }
                    current_vpc["availability_zones"].append(current_az)

            subnet = {
                "id": node["id"],
                "name": node.get("name"),
                "resources": []
            }

            public = metadata.get("map_public_ip_on_launch", False)

            if isinstance(public, str):
                public = public.lower() == "true"

            if public:
                if current_az:
                    current_az["public_subnets"].append(subnet)
            else:
                if current_az:
                    current_az["private_subnets"].append(subnet)

            current_subnet = subnet

        #
        # Resource
        #
        else:
            if current_subnet:
                current_subnet["resources"].append({
                    "id": node["id"],
                    "type": node["type"],
                    "name": node.get("name"),
                    "metadata": metadata
                })

        #
        # Continue traversal
        #
        for child in node["children"]:
            self._walk(
                child,
                current_vpc,
                current_az,
                current_subnet,
                vpcs
            )