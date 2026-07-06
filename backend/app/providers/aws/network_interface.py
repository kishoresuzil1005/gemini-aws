import boto3
import logging
logger = logging.getLogger(__name__)

class NetworkInterfaceDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('ec2', region_name=region)
            paginator = client.get_paginator('describe_network_interfaces')
            interfaces = []
            for page in paginator.paginate():
                for eni in page.get('NetworkInterfaces', []):
                    security_groups = [sg['GroupId'] for sg in eni.get('Groups', [])]
                    attachment = eni.get('Attachment', {})
                    interfaces.append({'resource_id': eni['NetworkInterfaceId'], 'resource_type': 'NetworkInterface', 'region': region, 'name': eni['NetworkInterfaceId'], 'status': eni.get('Status'), 'provider': 'AWS', 'metadata': {'description': eni.get('Description'), 'interface_type': eni.get('InterfaceType'), 'private_ip': eni.get('PrivateIpAddress'), 'mac_address': eni.get('MacAddress'), 'subnet_id': eni.get('SubnetId'), 'vpc_id': eni.get('VpcId'), 'owner_id': eni.get('OwnerId'), 'attachment': attachment, 'security_groups': security_groups}, 'dependencies': ([{'type': 'VPC', 'id': eni.get('VpcId')}] if eni.get('VpcId') else []) + ([{'type': 'Subnet', 'id': eni.get('SubnetId')}] if eni.get('SubnetId') else []) + [{'type': 'SecurityGroup', 'id': g.get('GroupId')} for g in eni.get('Groups', []) if g.get('GroupId')]})
            return interfaces
        except Exception:
            logger.exception('Network Interface discovery failed for region %s', region)
            return []