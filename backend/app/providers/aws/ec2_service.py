from typing import List, Dict, Any
from .aws_client import AWSClientManager

class EC2Service:
    def __init__(self, client_manager: AWSClientManager):
        self.client = client_manager.get_client("ec2")

    def describe_instances(self) -> List[Dict[str, Any]]:
        print("[EC2Service] Discovering EC2 instances...")
        response = self.client.describe_instances()
        instances = []
        for reservation in response.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                instances.append(instance)
        return instances

    def start_instance(self, instance_id: str):
        print(f"[EC2Service] Starting EC2 instance {instance_id}...")
        return self.client.start_instances(InstanceIds=[instance_id])

    def stop_instance(self, instance_id: str):
        print(f"[EC2Service] Stopping EC2 instance {instance_id}...")
        return self.client.stop_instances(InstanceIds=[instance_id])

    def reboot_instance(self, instance_id: str):
        print(f"[EC2Service] Rebooting EC2 instance {instance_id}...")
        return self.client.reboot_instances(InstanceIds=[instance_id])

    def terminate_instance(self, instance_id: str):
        print(f"[EC2Service] Terminating EC2 instance {instance_id}...")
        return self.client.terminate_instances(InstanceIds=[instance_id])
