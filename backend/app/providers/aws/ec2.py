from .auth import get_aws_client

class EC2Adapter:
    def __init__(self, session):
        self.client = get_aws_client("ec2")
    
    def describe_instances(self):
        return self.client.describe_instances()
