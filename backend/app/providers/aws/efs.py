import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

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
                    
                    dependencies = []
                    kms_key = fs.get('KmsKeyId')
                    if kms_key:
                        dependencies.append(ResourceDependency(type='KMSKey', id=kms_key))
                        
                    lifecycle_policies = []
                    try:
                        lp_resp = client.describe_lifecycle_configuration(FileSystemId=fs_id)
                        lifecycle_policies = lp_resp.get('LifecyclePolicies', [])
                    except Exception: pass
                    
                    res = NormalizedResource(
                        resource_id=fs_arn or fs_id,
                        resource_type='EFSFileSystem',
                        region=region,
                        name=name,
                        status=fs.get('LifeCycleState', 'Unknown'),
                        metadata={
                            'arn': fs_arn,
                            'file_system_id': fs_id,
                            'performance_mode': fs.get('PerformanceMode', 'generalPurpose'),
                            'throughput_mode': fs.get('ThroughputMode', 'bursting'),
                            'size_bytes': fs.get('SizeInBytes', {}).get('Value', 0)
                        },
                        security={
                            'encrypted': fs.get('Encrypted', False),
                            'kms_key_id': kms_key
                        },
                        configuration={
                            'provisioned_throughput': fs.get('ProvisionedThroughputInMibps', 0),
                            'lifecycle_policies': lifecycle_policies
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    resources.append(res.dict())
                    
                    try:
                        mt_paginator = client.get_paginator('describe_mount_targets')
                        for mt_page in mt_paginator.paginate(FileSystemId=fs_id):
                            for mt in mt_page.get('MountTargets', []):
                                mt_id = mt['MountTargetId']
                                
                                mt_dependencies = [ResourceDependency(type='EFSFileSystem', id=fs_arn or fs_id)]
                                subnet_id = mt.get('SubnetId')
                                if subnet_id:
                                    mt_dependencies.append(ResourceDependency(type='Subnet', id=subnet_id))
                                vpc_id = mt.get('VpcId')
                                if vpc_id:
                                    mt_dependencies.append(ResourceDependency(type='VPC', id=vpc_id))
                                eni_id = mt.get('NetworkInterfaceId')
                                if eni_id:
                                    mt_dependencies.append(ResourceDependency(type='NetworkInterface', id=eni_id))
                                    
                                security_groups = []
                                try:
                                    sg_resp = client.describe_mount_target_security_groups(MountTargetId=mt_id)
                                    security_groups = sg_resp.get('SecurityGroups', [])
                                    for sg in security_groups:
                                        mt_dependencies.append(ResourceDependency(type='SecurityGroup', id=sg))
                                except Exception: pass
                                
                                mt_res = NormalizedResource(
                                    resource_id=mt_id,
                                    resource_type='EFSMountTarget',
                                    region=region,
                                    name=f'{name}-mt-{mt_id}',
                                    status=mt.get('LifeCycleState', 'Unknown'),
                                    metadata={
                                        'mount_target_id': mt_id,
                                        'file_system_id': fs_id,
                                        'file_system_arn': fs_arn,
                                        'ip_address': mt.get('IpAddress', ''),
                                        'availability_zone': mt.get('AvailabilityZoneName', ''),
                                        'owner_id': mt.get('OwnerId', '')
                                    },
                                    security={
                                        'security_groups': security_groups
                                    },
                                    configuration={
                                        'subnet_id': subnet_id,
                                        'vpc_id': vpc_id,
                                        'network_interface_id': eni_id
                                    },
                                    tags={},
                                    dependencies=mt_dependencies
                                )
                                resources.append(mt_res.dict())
                    except Exception:
                        logger.exception('EFS mount targets failed for %s in region %s', fs_id, region)
        except Exception:
            logger.exception('EFS discovery failed for region %s', region)
        return resources