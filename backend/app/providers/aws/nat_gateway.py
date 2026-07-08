import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class NatGatewayDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('ec2', region_name=region)
            paginator = client.get_paginator('describe_nat_gateways')
            gateways = []
            
            for page in paginator.paginate():
                for nat in page.get('NatGateways', []):
                    tags = {t['Key']: t['Value'] for t in nat.get('Tags', [])}
                    name = tags.get('Name', nat['NatGatewayId'])
                    
                    dependencies = []
                    elastic_ips = []
                    network_interfaces = []
                    
                    for address in nat.get('NatGatewayAddresses', []):
                        if address.get('AllocationId'):
                            elastic_ips.append(address['AllocationId'])
                            dependencies.append(ResourceDependency(type='ElasticIP', id=address['AllocationId']))
                        if address.get('PublicIp'):
                            elastic_ips.append(address['PublicIp'])
                        if address.get('NetworkInterfaceId'):
                            network_interfaces.append(address['NetworkInterfaceId'])
                            dependencies.append(ResourceDependency(type='NetworkInterface', id=address['NetworkInterfaceId']))
                            
                    vpc_id = nat.get('VpcId')
                    subnet_id = nat.get('SubnetId')
                    if vpc_id:
                        dependencies.append(ResourceDependency(type='VPC', id=vpc_id))
                    if subnet_id:
                        dependencies.append(ResourceDependency(type='Subnet', id=subnet_id))
                        
                    res = NormalizedResource(
                        resource_id=nat['NatGatewayId'],
                        resource_type='NatGateway',
                        region=region,
                        name=name,
                        status=nat.get('State', 'Unknown'),
                        metadata={
                            'connectivity_type': nat.get('ConnectivityType'),
                            'elastic_ips': elastic_ips,
                            'network_interfaces': network_interfaces
                        },
                        configuration={
                            'vpc_id': vpc_id,
                            'subnet_id': subnet_id,
                            'failure_message': nat.get('FailureMessage')
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    gateways.append(res.dict())
                    
            return gateways
        except Exception:
            logger.exception('NAT Gateway discovery failed for region %s', region)
            return []