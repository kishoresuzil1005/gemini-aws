import boto3
import logging
from app.providers.aws.models import NormalizedResource, ResourceDependency

logger = logging.getLogger(__name__)

class AutoScalingDiscovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('autoscaling', region_name=region)
            paginator = client.get_paginator('describe_auto_scaling_groups')
            groups = []
            
            for page in paginator.paginate():
                for asg in page.get('AutoScalingGroups', []):
                    tags = {t['Key']: t['Value'] for t in asg.get('Tags', [])}
                    name = asg['AutoScalingGroupName']
                    
                    dependencies = []
                    instances = []
                    for instance in asg.get('Instances', []):
                        inst_id = instance['InstanceId']
                        instances.append(inst_id)
                        dependencies.append(ResourceDependency(type='EC2', id=inst_id))
                        
                    target_groups = list(asg.get('TargetGroupARNs', []))
                    for tg in target_groups:
                        dependencies.append(ResourceDependency(type='TargetGroup', id=tg))
                        
                    launch_template = None
                    if asg.get('LaunchTemplate'):
                        launch_template = asg['LaunchTemplate'].get('LaunchTemplateId')
                        
                    vpc_zones = asg.get('VPCZoneIdentifier', '').split(',')
                    for subnet in vpc_zones:
                        if subnet.strip():
                            dependencies.append(ResourceDependency(type='Subnet', id=subnet.strip()))

                    res = NormalizedResource(
                        resource_id=name,
                        resource_type='AutoScalingGroup',
                        region=region,
                        name=name,
                        status=asg.get('Status', 'Active'),
                        metadata={
                            'arn': asg.get('AutoScalingGroupARN'),
                            'min_size': asg.get('MinSize'),
                            'max_size': asg.get('MaxSize'),
                            'desired_capacity': asg.get('DesiredCapacity'),
                            'availability_zones': asg.get('AvailabilityZones', []),
                            'health_check_type': asg.get('HealthCheckType'),
                            'health_check_grace_period': asg.get('HealthCheckGracePeriod')
                        },
                        configuration={
                            'vpc_zone_identifier': asg.get('VPCZoneIdentifier'),
                            'launch_template': launch_template,
                            'suspended_processes': [p['ProcessName'] for p in asg.get('SuspendedProcesses', [])],
                            'instances': instances,
                            'target_groups': target_groups
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    groups.append(res.dict())
                    
            return groups
        except Exception:
            logger.exception('Auto Scaling discovery failed for region %s', region)
            return []