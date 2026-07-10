from typing import List, Dict, Any
from .aws_client import AWSClientManager

class S3Service:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("s3")

    def list_buckets(self) -> List[Dict[str, Any]]:
        response = self.client.list_buckets()
        return response.get("Buckets", [])

    def get_bucket_policy(self, bucket_name: str) -> str:
        try:
            response = self.client.get_bucket_policy(Bucket=bucket_name)
            return response.get("Policy", "")
        except Exception:
            return ""
