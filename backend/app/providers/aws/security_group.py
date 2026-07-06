import boto3
import logging
logger = logging.getLogger(__name__)

class SecurityGroupDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('ec2', region_name=region)
            paginator = client.get_paginator('describe_security_groups')
            security_groups = []
            for page in paginator.paginate():
                for sg in page.get('SecurityGroups', []):
                    security_groups.append({'resource_id': sg['GroupId'], 'resource_type': 'SecurityGroup', 'region': region, 'name': sg.get('GroupName'), 'provider': 'AWS', 'metadata': {'description': sg.get('Description'), 'vpc_id': sg.get('VpcId'), 'owner_id': sg.get('OwnerId'), 'ingress_rules': len(sg.get('IpPermissions', [])), 'egress_rules': len(sg.get('IpPermissionsEgress', []))}, 'dependencies': [{'type': 'VPC', 'id': sg.get('VpcId')}] if sg.get('VpcId') else []})
            return security_groups
        except Exception:
            logger.exception('Security Group discovery failed for region %s', region)
            return []