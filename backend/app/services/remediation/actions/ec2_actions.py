import logging
from app.providers.aws.auth import get_aws_client

logger = logging.getLogger("EC2Actions")


class EC2Actions:

    @staticmethod
    def stop_instance(account_id, instance_id):

        ec2 = get_aws_client(
            "ec2",
            account_id or 1
        )

        return ec2.stop_instances(
            InstanceIds=[instance_id]
        )

    @staticmethod
    def start_instance(account_id, instance_id):

        ec2 = get_aws_client(
            "ec2",
            account_id or 1
        )

        return ec2.start_instances(
            InstanceIds=[instance_id]
        )

    @staticmethod
    def reboot_instance(account_id, instance_id):

        ec2 = get_aws_client(
            "ec2",
            account_id or 1
        )

        ec2.reboot_instances(
            InstanceIds=[instance_id]
        )

        return {
            "InstanceId": instance_id,
            "Status": "rebooting"
        }
