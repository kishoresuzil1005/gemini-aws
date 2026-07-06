import boto3

class EBSDiscovery:

    @staticmethod
    def discover(region):
        try:
            client = boto3.client('ec2', region_name=region)
            response = client.describe_volumes()
            volumes = []
            for vol in response.get('Volumes', []):
                attachments_list = []
                for att in vol.get('Attachments', []):
                    if 'InstanceId' in att:
                        attachments_list.append(att['InstanceId'])
                volumes.append({'resource_id': vol['VolumeId'], 'resource_type': 'EBS', 'region': region, 'status': vol.get('State'), 'provider': 'AWS', 'metadata': {'size_gb': vol.get('Size'), 'attachments_list': attachments_list, 'attachments': len(vol.get('Attachments', []))}, 'dependencies': [{'type': 'EC2', 'id': attachment['InstanceId']} for attachment in vol.get('Attachments', []) if attachment.get('InstanceId')]})
            return volumes
        except Exception:
            return []