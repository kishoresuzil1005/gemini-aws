import boto3
import logging
logger = logging.getLogger(__name__)

class AutoScalingDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('autoscaling', region_name=region)
            paginator = client.get_paginator('describe_auto_scaling_groups')
            groups = []
            for page in paginator.paginate():
                for asg in page.get('AutoScalingGroups', []):
                    instances = [instance['InstanceId'] for instance in asg.get('Instances', [])]
                    target_groups = list(asg.get('TargetGroupARNs', []))
                    launch_template = None
                    if asg.get('LaunchTemplate'):
                        launch_template = asg['LaunchTemplate'].get('LaunchTemplateId')
                    groups.append({'resource_id': asg['AutoScalingGroupName'], 'resource_type': 'AutoScalingGroup', 'region': region, 'name': asg['AutoScalingGroupName'], 'provider': 'AWS', 'metadata': {'arn': asg.get('AutoScalingGroupARN'), 'min_size': asg.get('MinSize'), 'max_size': asg.get('MaxSize'), 'desired_capacity': asg.get('DesiredCapacity'), 'availability_zones': asg.get('AvailabilityZones', []), 'vpc_zone_identifier': asg.get('VPCZoneIdentifier'), 'launch_template': launch_template, 'instances': instances, 'target_groups': target_groups}, 'dependencies': []})
            return groups
        except Exception:
            logger.exception('Auto Scaling discovery failed for region %s', region)
            return []