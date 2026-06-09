from .auth import get_aws_client

class EC2Adapter:
    def __init__(self, cloud_account_id):
        self.client = get_aws_client("ec2", cloud_account_id)
    
    def describe_instances(self):
        return self.client.describe_instances()
