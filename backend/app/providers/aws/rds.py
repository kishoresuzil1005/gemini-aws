from .auth import get_aws_client

class RDSAdapter:
    def __init__(self, session):
        self.client = get_aws_client("rds")
    
    def describe_db_instances(self):
        # Implementation placeholder
        pass
