from .auth import get_aws_client

class RDSAdapter:
    def __init__(self, cloud_account_id):
        self.client = get_aws_client("rds", cloud_account_id)
    
    def describe_db_instances(self):
        return self.client.describe_db_instances()
