import boto3
from app.providers.aws.models import NormalizedResource, ResourceDependency
from .auth import get_aws_client

class EC2Discovery:
    @staticmethod
    def discover(region: str):
        try:
            client = boto3.client('ec2', region_name=region)
            response = client.describe_instances()
            instances = []
            
            for reservation in response.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    name = next((tag['Value'] for tag in instance.get('Tags', []) if tag['Key'] == 'Name'), instance['InstanceId'])
                    tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    
                    dependencies = []
                    ebs_volumes = []
                    
                    for bdm in instance.get('BlockDeviceMappings', []):
                        vol_id = bdm.get('Ebs', {}).get('VolumeId')
                        if vol_id:
                            ebs_volumes.append(vol_id)
                            dependencies.append(ResourceDependency(type='EBS', id=vol_id))
                            
                    vpc_id = instance.get('VpcId')
                    if vpc_id:
                        dependencies.append(ResourceDependency(type='VPC', id=vpc_id))
                        
                    subnet_id = instance.get('SubnetId')
                    if subnet_id:
                        dependencies.append(ResourceDependency(type='Subnet', id=subnet_id))
                        
                    for sg in instance.get('SecurityGroups', []):
                        dependencies.append(ResourceDependency(type='SecurityGroup', id=sg.get('GroupId')))
                        
                    iam_arn = instance.get('IamInstanceProfile', {}).get('Arn')
                    if iam_arn:
                        dependencies.append(ResourceDependency(type='IAM', id=iam_arn))
                        
                    enis = [eni.get('NetworkInterfaceId') for eni in instance.get('NetworkInterfaces', [])]
                    for eni in enis:
                        if eni:
                            dependencies.append(ResourceDependency(type='ENI', id=eni))

                    res = NormalizedResource(
                        resource_id=instance['InstanceId'],
                        resource_type='EC2',
                        region=region,
                        name=name,
                        status=instance.get('State', {}).get('Name', 'Unknown'),
                        metadata={
                            'instance_type': instance.get('InstanceType'),
                            'image_id': instance.get('ImageId'),
                            'platform': instance.get('PlatformDetails'),
                            'launch_time': str(instance.get('LaunchTime')),
                            'availability_zone': instance.get('Placement', {}).get('AvailabilityZone'),
                            'private_ip': instance.get('PrivateIpAddress'),
                            'public_ip': instance.get('PublicIpAddress'),
                            'architecture': instance.get('Architecture'),
                            'cpu_options': instance.get('CpuOptions', {})
                        },
                        security={
                            'iam_instance_profile': iam_arn,
                            'security_groups': [sg.get('GroupId') for sg in instance.get('SecurityGroups', [])]
                        },
                        configuration={
                            'vpc_id': vpc_id,
                            'subnet_id': subnet_id,
                            'ebs_volumes': ebs_volumes,
                            'enis': enis,
                            'placement_group': instance.get('Placement', {}).get('GroupName')
                        },
                        monitoring={
                            'monitoring_state': instance.get('Monitoring', {}).get('State')
                        },
                        tags=tags,
                        dependencies=dependencies
                    )
                    instances.append(res.dict())
                    
            return instances
        except Exception as e:
            print(f"Error in EC2Discovery: {e}")
            return []