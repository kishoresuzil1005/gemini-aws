from .auth import get_aws_client

class EKSAdapter:
    def __init__(self, session):
        self.client = get_aws_client("eks")
    
    def list_clusters(self):
        # Implementation placeholder
        pass
