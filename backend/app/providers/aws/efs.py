import boto3
import logging
logger = logging.getLogger(__name__)

class EFSDiscovery:

    @staticmethod
    def discover(region: str) -> list[dict]:
        resources = []
        try:
            client = boto3.client('efs', region_name=region)
            paginator = client.get_paginator('describe_file_systems')
            for page in paginator.paginate():
                for fs in page.get('FileSystems', []):
                    fs_id = fs['FileSystemId']
                    fs_arn = fs.get('FileSystemArn', '')
                    tags = {t['Key']: t['Value'] for t in fs.get('Tags', [])}
                    name = tags.get('Name', fs_id)
                    resources.append({'resource_id': fs_arn or fs_id, 'resource_type': 'EFSFileSystem', 'region': region, 'name': name, 'provider': 'AWS', 'metadata': {'arn': fs_arn, 'file_system_id': fs_id, 'lifecycle_state': fs.get('LifeCycleState'), 'performance_mode': fs.get('PerformanceMode', 'generalPurpose'), 'throughput_mode': fs.get('ThroughputMode', 'bursting'), 'provisioned_throughput': fs.get('ProvisionedThroughputInMibps', 0), 'encrypted': fs.get('Encrypted', False), 'kms_key_id': fs.get('KmsKeyId', ''), 'size_bytes': fs.get('SizeInBytes', {}).get('Value', 0), 'tags': tags}, 'dependencies': []})
                    try:
                        mt_paginator = client.get_paginator('describe_mount_targets')
                        for mt_page in mt_paginator.paginate(FileSystemId=fs_id):
                            for mt in mt_page.get('MountTargets', []):
                                mt_id = mt['MountTargetId']
                                resources.append({'resource_id': mt_id, 'resource_type': 'EFSMountTarget', 'region': region, 'name': f'{name}-mt-{mt_id}', 'provider': 'AWS', 'metadata': {'mount_target_id': mt_id, 'file_system_id': fs_id, 'file_system_arn': fs_arn, 'lifecycle_state': mt.get('LifeCycleState'), 'subnet_id': mt.get('SubnetId', ''), 'vpc_id': mt.get('VpcId', ''), 'ip_address': mt.get('IpAddress', ''), 'network_interface_id': mt.get('NetworkInterfaceId', ''), 'availability_zone': mt.get('AvailabilityZoneName', ''), 'owner_id': mt.get('OwnerId', '')}, 'dependencies': []})
                    except Exception:
                        logger.exception('EFS mount targets failed for %s in region %s', fs_id, region)
        except Exception:
            logger.exception('EFS discovery failed for region %s', region)
        return resources