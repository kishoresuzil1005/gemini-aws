from typing import Dict, Any
from ..aws_client import AWSClientManager
from ..ec2_service import EC2Service

class AWSActionAdapter:
    """
    Connects the Phase 11 Mission Engine / Workflow Engine directly to the 
    real AWS SDKs, allowing Missions to execute real changes on infrastructure.
    """
    def __init__(self, client_manager: AWSClientManager):
        self.ec2 = EC2Service(client_manager)

    def execute_action(self, action_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[AWSActionAdapter] Executing {action_name} against real AWS Provider...")
        
        try:
            if action_name == "start_ec2_instance":
                self.ec2.start_instance(payload["instance_id"])
                return {"status": "SUCCESS"}
            elif action_name == "stop_ec2_instance":
                self.ec2.stop_instance(payload["instance_id"])
                return {"status": "SUCCESS"}
            else:
                return {"status": "FAILED", "reason": f"Action {action_name} not supported."}
        except Exception as e:
            return {"status": "FAILED", "reason": str(e)}
