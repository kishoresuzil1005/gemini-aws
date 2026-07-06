from .auth import get_aws_client
import boto3

class EC2Discovery:

    @staticmethod
    def discover(region):
        client = boto3.client('ec2', region_name=region)
        response = client.describe_instances()
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                vols = []
                for bdm in instance.get('BlockDeviceMappings', []):
                    ebs_sec = bdm.get('Ebs', {})
                    vol_id = ebs_sec.get('VolumeId')
                    if vol_id:
                        vols.append(vol_id)
                instances.append({'resource_id': instance['InstanceId'], 'resource_type': 'EC2', 'region': region, 'status': instance['State']['Name'], 'provider': 'AWS', 'metadata': {'instance_type': instance.get('InstanceType'), 'launch_time': str(instance.get('LaunchTime')), 'subnet_id': instance.get('SubnetId'), 'vpc_id': instance.get('VpcId'), 'security_groups': [sg.get('GroupId') for sg in instance.get('SecurityGroups', [])], 'iam_instance_profile': instance.get('IamInstanceProfile', {}).get('Arn'), 'ebs_volumes': vols}, 'dependencies': ([{'type': 'VPC', 'id': instance.get('VpcId')}] if instance.get('VpcId') else []) + ([{'type': 'Subnet', 'id': instance.get('SubnetId')}] if instance.get('SubnetId') else []) + [{'type': 'SecurityGroup', 'id': sg.get('GroupId')} for sg in instance.get('SecurityGroups', [])] + [{'type': 'EBS', 'id': v} for v in vols] + ([{'type': 'IAM', 'id': instance.get('IamInstanceProfile', {}).get('Arn')}] if instance.get('IamInstanceProfile', {}).get('Arn') else [])})
        return instances

    @staticmethod
    def get_instances(region):
        client = boto3.client('ec2', region_name=region)
        response = client.describe_instances()
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append({'status': instance['State']['Name'], 'region': region, 'provider': 'AWS', 'metadata': {'instance_id': instance['InstanceId'], 'instance_type': instance['InstanceType'], 'public_ip': instance.get('PublicIpAddress'), 'private_ip': instance.get('PrivateIpAddress')}, 'dependencies': ([{'type': 'VPC', 'id': instance.get('VpcId')}] if instance.get('VpcId') else []) + ([{'type': 'Subnet', 'id': instance.get('SubnetId')}] if instance.get('SubnetId') else []) + [{'type': 'SecurityGroup', 'id': sg.get('GroupId')} for sg in instance.get('SecurityGroups', [])] + [{'type': 'EBS', 'id': v} for v in vols] + ([{'type': 'IAM', 'id': instance.get('IamInstanceProfile', {}).get('Arn')}] if instance.get('IamInstanceProfile', {}).get('Arn') else [])})
        return instances