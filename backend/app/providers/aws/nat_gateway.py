import boto3
import logging

logger = logging.getLogger(__name__)


class NatGatewayDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client("ec2", region_name=region)
            paginator = client.get_paginator("describe_nat_gateways")
            gateways = []
            for page in paginator.paginate():
                for nat in page.get("NatGateways", []):
                    elastic_ips = []
                    network_interfaces = []
                    for address in nat.get("NatGatewayAddresses", []):
                        if address.get("AllocationId"):
                            elastic_ips.append(address["AllocationId"])
                        if address.get("PublicIp"):
                            elastic_ips.append(address["PublicIp"])
                        if address.get("NetworkInterfaceId"):
                            network_interfaces.append(address["NetworkInterfaceId"])
                    gateways.append({
                        "resource_id": nat["NatGatewayId"],
                        "resource_type": "NatGateway",
                        "region": region,
                        "name": nat["NatGatewayId"],
                        "vpc_id": nat.get("VpcId"),
                        "subnet_id": nat.get("SubnetId"),
                        "state": nat.get("State"),
                        "connectivity_type": nat.get("ConnectivityType"),
                        "elastic_ips": elastic_ips,
                        "network_interfaces": network_interfaces
                    })
            return gateways
        except Exception:
            logger.exception("NAT Gateway discovery failed for region %s", region)
            return []
