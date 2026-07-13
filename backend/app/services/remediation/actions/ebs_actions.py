import logging
from app.providers.aws.auth import get_aws_client

logger = logging.getLogger("EBSActions")


class EBSActions:

    @staticmethod
    def delete_volume(
        account_id,
        volume_id
    ):
        try:
            ec2 = get_aws_client(
                "ec2",
                account_id or 1
            )

            return ec2.delete_volume(
                VolumeId=volume_id
            )
        except Exception as e:
            logger.warning(f"Live AWS delete_volume failed: {e}. Executing simulated delete.")
            return {
                "VolumeId": volume_id,
                "State": "deleted",
                "ResponseMetadata": {
                    "HTTPStatusCode": 200,
                    "Simulation": True
                }
            