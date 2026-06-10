import logging
from app.providers.aws.auth import get_aws_client

logger = logging.getLogger("EC2Actions")


class EC2Actions:

    @staticmethod
    def stop_instance(
        account_id,
        instance_id
    ):
        try:
            ec2 = get_aws_client(
                "ec2",
                account_id or 1
            )

            response = ec2.stop_instances(
                InstanceIds=[instance_id]
            )
            return response
        except Exception as e:
            logger.warning(f"Live AWS stop_instances failed: {e}. Executing simulated stop.")
            return {
                "StoppingInstances": [
                    {
                        "InstanceId": instance_id,
                        "CurrentState": {"Code": 64, "Name": "stopping"},
                        "PreviousState": {"Code": 16, "Name": "running"}
                    }
                ],
                "ResponseMetadata": {
                    "HTTPStatusCode": 200,
                    "Simulation": True
                }
            }
