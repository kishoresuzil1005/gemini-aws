import boto3

class S3Discovery:

    @staticmethod
    def discover():
        client = boto3.client('s3')
        response = client.list_buckets()
        resources = []
        for bucket in response['Buckets']:
            resources.append({'resource_id': bucket['Name'], 'resource_type': 'S3', 'provider': 'AWS', 'metadata': {'created': str(bucket['CreationDate'])}, 'dependencies': []})
        return resources