import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class SubnetDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('ec2', region_name=region)
            paginator = client.get_paginator('describe_subnets')
            subnets = []
            
            for page in paginator.paginate():
                for subnet in page.get('Subnets', []):
                    tags = {t['Key']: t['Value'] for t in subnet.get('Tags', [])}
                    name = tags.get('Name', subnet['SubnetId'])
                    
                    dependencies = []
                    vpc_id = subnet.get('VpcId')
                    if vpc_id:
                        dependencies.append(ResourceDependency(type='VPC', id=vpc_id))

                    res = NormalizedResource(
                        resource_id=subnet['SubnetId'],
                        resource_type='Subnet',
                        region=region,
                        name=name,
                        status=subnet.get('State', 'Unknown'),
                        metadata={
                            'cidr_block': subnet.get('CidrBlock'),
                            'availability_zone': subnet.get('AvailabilityZone'),
                            'available_ip_count': subnet.get('AvailableIpAddressCount'),
                        },
                        configuration={
                            'vpc_id': vpc_id,
                            'default_for_az': subnet.get('DefaultForAz', False),
                            'map_public_ip': subnet.get('MapPublicIpOnLaunch', False),
                            'assign_ipv6_address_on_creation': subnet.get('AssignIpv6AddressOnCreation', False)
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    subnets.append(res.dict())
                    
            return subnets
        except Exception:
            logger.exception('Subnet discovery failed for region %s', region)
            return []