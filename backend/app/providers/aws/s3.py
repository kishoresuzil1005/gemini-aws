from .auth import get_aws_client

class S3Adapter:
    def __init__(self, cloud_account_id):
        self.client = get_aws_client("s3", cloud_account_id)
    
    def list_buckets(self):
        return self.client.list_buckets()
