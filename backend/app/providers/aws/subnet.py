import boto3
import logging
logger = logging.getLogger(__name__)

class SubnetDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('ec2', region_name=region)
            paginator = client.get_paginator('describe_subnets')
            subnets = []
            for page in paginator.paginate():
                for subnet in page.get('Subnets', []):
                    subnets.append({'resource_id': subnet['SubnetId'], 'resource_type': 'Subnet', 'region': region, 'name': subnet['SubnetId'], 'status': subnet.get('State'), 'provider': 'AWS', 'metadata': {'vpc_id': subnet.get('VpcId'), 'availability_zone': subnet.get('AvailabilityZone'), 'cidr_block': subnet.get('CidrBlock'), 'available_ip_count': subnet.get('AvailableIpAddressCount'), 'default_for_az': subnet.get('DefaultForAz', False), 'map_public_ip': subnet.get('MapPublicIpOnLaunch', False)}, 'dependencies': [{'type': 'VPC', 'id': subnet.get('VpcId')}] if subnet.get('VpcId') else []})
            return subnets
        except Exception:
            logger.exception('Subnet discovery failed for region %s', region)
            return []