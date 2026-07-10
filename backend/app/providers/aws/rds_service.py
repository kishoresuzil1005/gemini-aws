from typing import List, Dict, Any
from .aws_client import AWSClientManager

class RDSService:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("rds")

    def describe_db_instances(self) -> List[Dict[str, Any]]:
        response = self.client.describe_db_instances()
        return response.get("DBInstances", [])

    def start_db_instance(self, db_instance_identifier: str):
        return self.client.start_db_instance(DBInstanceIdentifier=db_instance_identifier)

    def stop_db_instance(self, db_instance_identifier: str):
        return self.client.stop_db_instance(DBInstanceIdentifier=db_instance_identifier)
