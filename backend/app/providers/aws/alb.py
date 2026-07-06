import boto3
import logging
logger = logging.getLogger(__name__)

class ALBDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('elbv2', region_name=region)
            paginator = client.get_paginator('describe_load_balancers')
            lbs = []
            for page in paginator.paginate():
                for lb in page.get('LoadBalancers', []):
                    lbs.append({'resource_id': lb['LoadBalancerArn'], 'resource_type': 'ALB', 'region': region, 'name': lb['LoadBalancerName'], 'status': lb.get('State', {}).get('Code'), 'provider': 'AWS', 'metadata': {'dns_name': lb.get('DNSName'), 'scheme': lb.get('Scheme'), 'vpc_id': lb.get('VpcId')},  'dependencies': ([{'type': 'VPC', 'id': lb.get('VpcId')}] if lb.get('VpcId') else []) + [{'type': 'Subnet', 'id': az.get('SubnetId')} for az in lb.get('AvailabilityZones', []) if az.get('SubnetId')] + [{'type': 'SecurityGroup', 'id': sg} for sg in lb.get('SecurityGroups', [])]})
            return lbs
        except Exception:
            logger.exception('ALB discovery failed for region %s', region)
            return []