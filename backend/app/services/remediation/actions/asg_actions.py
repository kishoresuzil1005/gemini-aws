import logging
from app.providers.aws.auth import get_aws_client

logger = logging.getLogger("ASGActions")


class ASGActions:

    @staticmethod
    def resume_processes(account_id, asg_name):
        try:
            autoscaling = get_aws_client("autoscaling", account_id or 1)
            return autoscaling.resume_processes(AutoScalingGroupName=asg_name)
        except Exception as e:
            logger.warning(f"Live AWS resume_processes failed: {e}. Executing simulated resume.")
            return {"AutoScalingGroupName": asg_name, "Simulation": True}